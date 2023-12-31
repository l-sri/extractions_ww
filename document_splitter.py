import json
import os
import yaml

def load_config(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
    
import re
import os

def split_document_into_sections(document_name, input_toc_folder, input_txt_folder, output_txt_folder):
    """Splits a document into sections based on the provided JSON structure."""

    print(f"Splitting {document_name}")

    # Construct file paths for the JSON and text files
    json_file_path = os.path.join(input_toc_folder, f"{document_name}.json")
    text_file_path = os.path.join(input_txt_folder, f"{document_name}.txt")

    # Load the TOC content using regex (non-recursive pattern)
    with open(json_file_path, "r") as f:
        json_content = f.read()
        pattern = r'"([^"]*)":\s*\[(.*?)\]'  # Match key-value pairs directly
        matches = re.findall(pattern, json_content)

    # print("mathches: ", matches )
    toc = {}
    for key, value_str in matches:
        # print(key, value_str)
        values = []
        for sublist_str in value_str.split("], "):  # Split nested lists
            for item in sublist_str.strip("[]").split(","):
                try:
                    values.append(int(item))  # Convert to int if possible
                except ValueError:
                    values.append(None)  # Handle null values
        if key in toc:
            toc[key].append(values)  # Append to existing list for duplicates
        else:
            toc[key] = [values]

    # print("toc: ", toc)

    # Read the text content of the document
    with open(text_file_path, "r") as f:
        text = f.read()

    # Split the text into pages using the specified delimiter
    pages = text.split("Page Number ")[1:]
    pages = ["Page Number " + page for page in pages]

    # Iterate through each section in the TOC
    for section_name in toc.keys():
        for page_range in toc[section_name]:
            # Extract and adjust page range indices for zero-based indexing
            start_page = page_range[0] - 1
            end_page = page_range[1] if page_range[1] else len(pages)  # Handle open-ended ranges

            # Extract the text for the current section from the pages list
            section_text = "\n".join(pages[start_page:end_page])

            # Construct the output file path, incorporating start and end pages
            output_file_path = os.path.join(output_txt_folder, f"{document_name}_{section_name}_{start_page+1}_{end_page}.txt")

            # print(f"section_name: {section_name}\npage_range: {page_range}\noutput_file_path: {output_file_path}\n")

            # Write the section text to the output file
            with open(output_file_path, "w") as f:
                f.write(section_text)

    
if __name__ == "__main__":

    config_file = "./config.yaml"

    if os.path.exists(config_file):
        print(f"{config_file} exists!")
    else:
        print(f"{config_file} does not exist.")

    # Load parameters from config.yml
    config = load_config(config_file)

    if config is not None:
        pdf_input_folders = config.get("input_folders")
        # Proceed with using pdf_input_folders
    else:
        print("Error loading config file!")
        # Handle the error gracefully, e.g., exit or provide a default value

    # Specify input and output folder paths (replace with actual paths)
    input_toc_folder = config.get("toc_json")
    input_txt_folder = config.get("extracted_txt")
    output_txt_folder = config.get("final_ext_txt")

    # List of document names to process (replace with actual names)
    document_names = config.get("split_docs")
    

    # Iterate through each document and split it into sections
    for document_name in document_names:
        split_document_into_sections(document_name, input_toc_folder, input_txt_folder, input_txt_folder)
