import sys
import os
import pandas as pd
import argparse
import yaml
parent_dir = "."
sys.path.append(parent_dir)
from utils.docAI_extraction import process_local_document_in_chunks
from utils.table_extraction import get_latex_tables_camelot, get_pdf_table_latex, extract_and_clean_tables
# import argo_utils

def print_yaml_content(file_path):
    """Prints the content of a YAML file in a human-readable format."""

    try:
        with open(file_path, "r") as file:
            yaml_data = yaml.safe_load(file)

        # Print the parsed YAML data in a user-friendly way
        print(f"Content from {file_path}: \n")
        print(yaml.dump(yaml_data, default_flow_style=False))

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML file: {exc}")

def load_config(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def extract_pdf(input_folder, output_folder, redo_extract):
    
    files = os.listdir(input_folder)

    # Filter out the pdf files
    pdf_files = []
    for file in files:
        if file.endswith(".pdf"):
            pdf_files.append(file)


    for pdf_file in pdf_files:

        print("-"*50)
        print("Processing: ", pdf_file)
        document_hash = pdf_file.split('.pdf')[0]
        file_path = os.path.join(input_folder, pdf_file)
        
        # latex_tables = get_latex_tables_camelot(file_path)
        # print(f'Tables : {latex_tables}')
        page_data, tables, doc_content = extract_and_clean_tables(file_path)
        # print(doc_content)


        output_path = pdf_output_folder + document_hash + ".txt"
        print(f"Number of pages in {pdf_file}: {len(doc_content)}")
        print(f"Saving extracted text to {output_path}")
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

    # Get the input and output folder for pdfs
    pdf_input_folder = config.get("raw_data")
    pdf_output_folder = config.get("extracted_txt")
    print(f"Processing pdf files from {pdf_input_folder}")
    
    # GCP creds/Info
    project_id = config.get("project_id")
    location = config.get("location")
    processor_id = config.get("processor_id")
    mime_type = config.get("mime_type")

    # Process paramaters
    redo_extract = config.get("redo_extract")

    # Check to make sure input folder exists and create output folder if it does not exist
    if not os.path.exists(pdf_input_folder):
        print(f"{pdf_input_folder} does not exists!")
    
    for path in [pdf_output_folder]:
        if not os.path.exists(path):
            os.mkdir(path)

    
    extract_pdf(input_folder = pdf_input_folder, output_folder = pdf_output_folder, redo_extract = redo_extract)
    print("*"*100)
# #python3 pdf_parser.py data/invoices/ data/purchase\ orders/