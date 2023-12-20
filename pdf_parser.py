import sys
import os
import pandas as pd
import argparse
parent_dir = "."
sys.path.append(parent_dir)
from utils.docAI_extraction import process_local_document_in_chunks
from utils.table_extraction import get_latex_tables_camelot, get_pdf_table_latex, extract_and_clean_tables
# import argo_utils

# # cred_path = "llmapps-creds.json"
# cred_path = "docai-creds.json"
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download pdf and excel files to a local directory."
    )

    # Adding argument for the configuration file
    # parser.add_argument("--pdf_folders", type=str, default="data/pdf_files/", help="URL to parse")
    # args = parser.parse_args()
    # if args.pdf_folders:
    #     pdf_folders = args.pdf_folders

    pdf_folders = [str(arg) for arg in sys.argv[1:]]
    pdf_folders.append("./data/input/")
    print(pdf_folders)
    project_id = "llmapps"
    location = "us"
    processor_id = "c0ec8848a9756a33"
    mime_type = "application/pdf"
    

    output_folder = "data/processed_files/"
    pdf_output_folder = "data/processed_files/pdf_output/"
    for path in [output_folder, pdf_output_folder]:
        if not os.path.exists(path):
            os.mkdir(path)

    for pdf_folder in pdf_folders:
            
            pdf_files = os.listdir(pdf_folder)
            pdf_sample_size = len(pdf_files)

            for pdf_file in pdf_files[:pdf_sample_size]:
                print("Processing: ", pdf_file)
                document_hash = pdf_file.split('.pdf')[0]
                file_path = os.path.join(pdf_folder, pdf_file)
                # latex_tables = get_latex_tables_camelot(file_path)
                # print(f'Tables : {latex_tables}')
                page_data, tables, doc_content = extract_and_clean_tables(file_path)
                # print(doc_content)
                

                # output_path = pdf_output_folder + document_hash + '.txt'#"last_4_pages.txt"
                # cnt = 1

                output_path = pdf_output_folder + document_hash + ".txt"
                print(f"Number of pages in {pdf_file}: {len(doc_content)}")
                file = open(output_path, "w")
                
                # for dc in doc_content:
                for i, dc in enumerate(doc_content):
                    file.write(f"Page Number {i+1}:\n")
                    file.write("\n")
                    for i in range(len(dc)):#item in dc:
                        item = dc[i]
                        
                        # print('Writing tables')
                        # print(i, item)
                        if i > 0:
                            for table in item:
                                file.write(table)
                        else:
                            # print('Writing text')
                            file.write(item)
                        file.write("\n")
                        # print(item)
                    file.write("\n")
                file.close()


                # print(f'Page Data : {page_data}')
                # print(f'Tables : {tables}')
                # print(page_data, tables)
                # output, text_data = process_local_document_in_chunks(
                #     project_id, location, processor_id, file_path, mime_type
                # )
                # print(f'Text data : {text_data}')
                # output_path = pdf_output_folder + document_hash + ".txt"
                # #+ str(chunk_index) + ".txt"
                # file = open(output_path, "a")
                # # curr_chunk_output = output#[chunk_index]                
                # file.writelines(output)
                
                # file.close()

#python3 pdf_parser.py data/invoices/ data/purchase\ orders/