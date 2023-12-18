from __future__ import annotations
from collections.abc import Sequence
from io import BytesIO
import traceback
import time

from google.api_core.client_options import ClientOptions
from google.cloud import documentai  # type: ignore
from google.cloud import storage  # type: ignore
from PyPDF2 import PdfReader, PdfWriter
import pandas as pd
import hashlib

pd.set_option("display.max_colwidth", None)


def extract_pdf_chunk(pdf_reader: PdfReader, start_page: int, end_page: int) -> bytes:
    try:
        writer = PdfWriter()

        for page_number in range(start_page - 1, end_page):
            writer.add_page(pdf_reader.pages[page_number])

        chunk_pdf_content = BytesIO()
        writer.write(chunk_pdf_content)
        chunk_pdf_content.seek(0)
    except Exception as e:
        # Handle the exception here
        traceback.print_exc()
        print("An error occurred:", str(e))

    return chunk_pdf_content.getvalue()


def process_document(
    project_id: str,
    location: str,
    processor_id: str,
    pdf_reader: PdfReader,
    mime_type: str,
    start_page: int,
    end_page: int,
) -> documentai.Document:
    try:
        # You must set the api_endpoint if you use a location other than 'us'.
        opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")

        client = documentai.DocumentProcessorServiceClient(client_options=opts)

        # The full resource name of the processor, e.g.:
        # projects/project_id/locations/location/processor/processor_id
        name = client.processor_path(project_id, location, processor_id)

        # Extract the relevant pages for the current chunk
        chunk_pdf_content = extract_pdf_chunk(pdf_reader, start_page, end_page)

        # Load Binary Data into Document AI RawDocument Object
        raw_document = documentai.RawDocument(content=chunk_pdf_content, mime_type=mime_type)

        print(f"About to process {start_page} - {end_page}")
        # Configure the process request
        request = documentai.ProcessRequest(name=name, raw_document=raw_document)
        # print(f'Request : {request}')
        # print('---------')
        result = client.process_document(request=request)
    except Exception as e:
        # Handle the exception here
        traceback.print_exc()
        print(f"An error occurred while processing pages {start_page} to {end_page}:", str(e))
        return None
    return result.document


def layout_to_text(layout: documentai.Document.Page.Layout, text: str) -> str:
    """
    Document AI identifies text in different parts of the document by their
    offsets in the entirety of the document's text. This function converts
    offsets to a string.
    """
    response = ""
    # If a text segment spans several lines, it will
    # be stored in different text segments.
    for segment in layout.text_anchor.text_segments:
        start_index = int(segment.start_index)
        end_index = int(segment.end_index)
        response += text[start_index:end_index]
    return response


def print_table_rows(
    table_rows: Sequence[documentai.Document.Page.Table.TableRow], text: str
) -> str:
    output = ""
    for table_row in table_rows:
        row_text = ""
        for cell in table_row.cells:
            cell_text = layout_to_text(cell.layout, text)
            row_text += f"{repr(cell_text.strip())} | "
        output += row_text + "\n"
    return output


def extract_text_data(page: documentai.Document.Page, text: str) -> (list[list[str]], list[int]):
    # Create a dictionary of tables in both cell and row format, using which we can compare
    # text lines to see whether that line of text belongs to a table, and figure out which table
    # it belongs to.
    all_table_cells = {}
    all_table_rows = {}
    table_info = []
    sorted_table_info = []
    table_dimensions = []
    sorted_tables = []
    print(f'Tables : {page.tables}')
    for i, table in enumerate(page.tables):
        # getting min and max  x,y coordinates for the table
        min_x, min_y, max_x, max_y = table_coordinates(table)
        dimensions = (min_x, min_y, max_x, max_y)

        table_cells = []
        table_rows = []
        for table_row in table.header_rows:
            process_table_row(text, table_cells, table_rows, table_row)
        for table_row in table.body_rows:
            process_table_row(text, table_cells, table_rows, table_row)
        all_table_cells[i] = table_cells
        all_table_rows[i] = table_rows

        table_info.append((table_rows, dimensions, i))

    # sort the tables based on the min_y coordinate
    sorted_table_info = sorted(table_info, key=lambda x: x[1][1])
    for stl in sorted_table_info:
        sorted_tables.append((stl[0], stl[1][0], stl[1][1], stl[2]))
    # list of coordinates for all tables
    table_dimensions = [element[1] for element in sorted_table_info]

    text_lines_only = []
    sorted_text_lines_only = []
    for l, line in enumerate(page.lines):
        line_in_text_block = False
        for td in table_dimensions:
            # check if line is inside a table
            if is_line_inside_current_text_block(line, td):
                line_in_text_block = True
                break
        # append the line once you confirm its not part of a table
        if line_in_text_block == False:
            text_lines_only.append(
                (
                    layout_to_text(line.layout, text),
                    line.layout.bounding_poly.vertices[0].x,
                    line.layout.bounding_poly.vertices[0].y,
                    l,
                )
            )

    sorted_text_lines_only = sorted(text_lines_only, key=lambda x: (50 * x[2] + x[1]))

    return sorted_tables, sorted_text_lines_only


def is_line_inside_current_text_block(line, td):
    return (
        line.layout.bounding_poly.vertices[0].y >= td[1]
        and line.layout.bounding_poly.vertices[0].y <= td[3]
    )


def table_coordinates(table):
    min_x, min_y = float("inf"), float("inf")
    max_x, max_y = float("-inf"), float("-inf")
    table_x = [table.layout.bounding_poly.vertices[x].x for x in range(4)]
    table_y = [table.layout.bounding_poly.vertices[y].y for y in range(4)]
    for j in range(4):
        min_x = min(min_x, table_x[j])
        min_y = min(min_y, table_y[j])
        max_x = max(max_x, table_x[j])
        max_y = max(max_y, table_y[j])
    return min_x, min_y, max_x, max_y


def process_table_row(
    text: str,
    table_cells: list[str],
    table_rows: list[str],
    table_row: documentai.Document.Page.Table.TableRow,
):
    row_text = ""
    for cell in table_row.cells:
        cell_text = layout_to_text(cell.layout, text)
        table_cells.append(cell_text)
        row_text += cell_text
    table_rows.append(row_text.strip())


def convert_table_to_dataframe(table, text):
    rows = []

    for table_row in table.header_rows:
        row = [layout_to_text(cell.layout, text).strip() for cell in table_row.cells]
        header = row
        rows.append(row)

    for table_row in table.body_rows:
        row = [layout_to_text(cell.layout, text).strip() for cell in table_row.cells]
        rows.append(row)

    # Convert rows into dataframe
    dataframe = pd.DataFrame(rows, columns=header)
    dataframe = dataframe.drop(0)
    latex_table = dataframe.style.to_latex()

    return latex_table


def process_chunk_toc(document: documentai.Document) -> list[str]:
    output = []
    try:
        text = document.text
        # print(text)
        output.extend(text.split("/n"))

    except Exception as e:
        # Handle the exception here
        traceback.print_exc()
        print("An error occurred:", str(e))
    return output


def process_chunk(chunk_index: int, chunk_size: int, document: documentai.Document) -> list[str]:
    # Read the table and form fields output from the processor
    # The form processor also contains OCR data. For more information
    # on how to parse OCR data please see the OCR sample.

    # For a full list of Document object attributes, please reference this page:
    # https://cloud.google.com/python/docs/reference/documentai/latest/google.cloud.documentai_v1.types.Document
    output = []
    raw_lines = []
    try:
        text = document.text
        raw_lines.extend(text.split("\n"))
        for page in document.pages:
            page_number = page.page_number + chunk_index * chunk_size
            page_text = f"Page Number {page_number}:\n"
            # Get the text data in the page in the form of a list of text blocks.
            tables, lines = extract_text_data(page, text)
            print(f'Page number {page_number}, {tables, lines}')
            print('********************')
            m = len(tables)
            n = len(lines)

            while m > 0 or n > 0:
                if m > 0 and n > 0:
                    if lines[0][2] < tables[0][2]:
                        n, page_text = transfer_line_to_output(page_text, lines, n)
                    else:
                        m, page_text = transfer_table_to_output(text, page_text, page, tables, m)
                elif m == 0:
                    while n > 0:
                        n, page_text = transfer_line_to_output(page_text, lines, n)
                else:
                    while m > 0:
                        m, page_text = transfer_table_to_output(text, page_text, page, tables, m)
            output.append(page_text.replace("\\n", "\n"))

    except Exception as e:
        # Handle the exception here
        traceback.print_exc()
        print("An error occurred:", str(e))
    return output, raw_lines


def transfer_table_to_output(text, output, page, tables, m):
    curr_table = tables.pop(0)
    dataframe = convert_table_to_dataframe(page.tables[curr_table[3]], text)
    output += f" \nTable: {dataframe}\n"
    m -= 1
    return m, output


def transfer_line_to_output(output, lines, n):
    curr_line = lines.pop(0)
    output += curr_line[0]
    n -= 1
    return n, output


def process_document_in_chunks(
    project_id: str,
    location: str,
    processor_id: str,
    file_path: str,
    mime_type: str,
    document_hash: str,
    gcp_dict: dict,
) -> list[str]:
    try:
        # Read the PDF and get the total number of pages
        print("Processing:", file_path.split("/")[-1])
        print("Hash:", document_hash)
        output = []
        text_data = []
        pdf_reader = None
        with open(file_path, "rb") as pdf_file:
            pdf_content = pdf_file.read()
            pdf_reader = PdfReader(BytesIO(pdf_content))
            num_pages = len(pdf_reader.pages)

        # output += f"There are {(num_pages)} page(s) in this document.\n"

        # Split the PDF into chunks of 15 pages
        chunk_size = 15
        num_chunks = (num_pages - 1) // chunk_size + 1

        for chunk_index in range(num_chunks):
            start_page = chunk_index * chunk_size + 1
            end_page = min((chunk_index + 1) * chunk_size, num_pages)

            bucket_name = gcp_dict["bucket_name"]
            dir_name = gcp_dict["directory"]
            bucket: storage.Bucket = gcp_dict["bucket_obj"]

            blob = bucket.blob(dir_name + document_hash + "/" + str(chunk_index) + ".pkl")
            # if document is previously seen
            if blob.exists():
                print("For chunk", chunk_index)
                s = time.time()
                retrieved_document = pd.read_pickle(
                    "gs://"
                    + bucket_name
                    + "/"
                    + dir_name
                    + document_hash
                    + "/"
                    + str(chunk_index)
                    + ".pkl"
                )
                e = time.time()
                print("Time taken to retrieve pkl:", e - s)
                s = time.time()
                curr_chunk_output, raw_lines_of_chunk = process_chunk(
                    chunk_index, chunk_size, retrieved_document
                )
                output += curr_chunk_output
                text_data += raw_lines_of_chunk
                e = time.time()
                print("Time taken to process document chunk:", e - s)
                print()

            # if the document is new
            else:
                # Online processing request to Document AI for the current chunk
                document = process_document(
                    project_id,
                    location,
                    processor_id,
                    pdf_reader,
                    mime_type,
                    start_page,
                    end_page,
                )

                if document is not None:
                    # Process the current chunk and print the results
                    curr_chunk_output, raw_lines_of_chunk = process_chunk(
                        chunk_index, chunk_size, document
                    )
                    text_data += raw_lines_of_chunk
                    # pd.to_pickle(
                    #     document,
                    #     "gs://"
                    #     + bucket_name
                    #     + "/"
                    #     + dir_name
                    #     + str(document_hash)
                    #     + "/"
                    #     + str(chunk_index)
                    #     + ".pkl",
                    # )
                    output += curr_chunk_output

    except Exception as e:
        # Handle the exception here
        traceback.print_exc()
        print("An error occurred:", str(e))
        # You can perform additional error handling or logging as needed

    return output, text_data


def process_local_document_in_chunks(
    project_id: str,
    location: str,
    processor_id: str,
    file_path: str,
    mime_type: str,
    # document_hash: str,
) -> list[str]:
    try:
        # Read the PDF and get the total number of pages
        print("Processing:", file_path.split("/")[-1])
        # print("Hash:", document_hash)
        output = []
        text_data = []
        pdf_reader = None
        with open(file_path, "rb") as pdf_file:
            pdf_content = pdf_file.read()
            pdf_reader = PdfReader(BytesIO(pdf_content))
            num_pages = len(pdf_reader.pages)

        # output += f"There are {(num_pages)} page(s) in this document.\n"

        # Split the PDF into chunks of 15 pages
        chunk_size = 15
        num_chunks = (num_pages - 1) // chunk_size + 1

        for chunk_index in range(num_chunks):
            start_page = chunk_index * chunk_size + 1
            end_page = min((chunk_index + 1) * chunk_size, num_pages)

            # Online processing request to Document AI for the current chunk
            document = process_document(
                project_id,
                location,
                processor_id,
                pdf_reader,
                mime_type,
                start_page,
                end_page,
            )

            if document is not None:
                # Process the current chunk and print the results
                curr_chunk_output, raw_lines_of_chunk = process_chunk(
                    chunk_index, chunk_size, document
                )
                text_data += raw_lines_of_chunk

                output += curr_chunk_output

    except Exception as e:
        # Handle the exception here
        traceback.print_exc()
        print("An error occurred:", str(e))
        # You can perform additional error handling or logging as needed

    return output, text_data
