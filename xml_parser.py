import os
import re

def process_folder(folder_path, output_folder="extracted_content"):
  os.makedirs(output_folder, exist_ok=True) # Create output folder if it doesn't exist

  for filename in os.listdir(folder_path):
    filepath = os.path.join(folder_path, filename)
    if not os.path.isfile(filepath):
      continue
    if not filename.endswith(".xml"):
      continue

    # Extract content from XML file
    with open(filepath, "r") as f:
      xml_data = f.read()
    content = re.sub(r'<[^>]*>', '', xml_data)
    content = re.sub(r'\s+', ' ', content).strip()

    # Create output filename and path
    output_filename = os.path.splitext(filename)[0] + ".txt"
    output_filepath = os.path.join(output_folder, output_filename)

    # Write extracted content to new file
    with open(output_filepath, "w") as f:
      f.write(content)
    print(f"Processed and extracted content to {output_filepath}")


# Set folder path for processing
input_folder = "./data/input/"
output_folder = "data/processed_files/xml_output/"
process_folder(input_folder, output_folder)