import os
import re
import random
from utils.helpers import load_config

def section_formatter(input_folder, output_folder):
   """Processes .txt files in the given folder, ensuring they have the required format."""
 
   regex = r"^(\d+\.\d+) --- (.+?)$"# Regex to match the required format

   for filename in os.listdir(input_folder):
       if filename.endswith(".txt"):
           input_file_path = os.path.join(input_folder, filename)
           output_file_path = os.path.join(output_folder, filename)

           with open(input_file_path, "r") as input_file:
               first_line = input_file.readline().strip()

               if re.match(regex, first_line):
                   # File already has the required format, copy it directly
                   with open(output_file_path, "w") as output_file:
                       output_file.write(input_file.read())
               else:
                   # Generate section number
                   s1 = random.randint(1, 10)
                   s2 = random.randint(1, 10)
                   section_number = f"{s1}.{s2}"

                   # Get file name without extension
                   file_name_without_ext = os.path.splitext(filename)[0]

                   # Modify the file content
                   content = input_file.read()
                   modified_content = f"{section_number} --- {file_name_without_ext}\n\n{first_line}\n{content}"

                   # Write the modified content to the output file
                   with open(output_file_path, "w") as output_file:
                       output_file.write(modified_content)


if __name__ == "__main__":

    config_file = "./config.yaml"

    if os.path.exists(config_file):
        print(f"{config_file} exists!")
    else:
        print(f"{config_file} does not exist.")

    # Load parameters from config.yml
    config = load_config(config_file)

    if config is not None:
        # Get the input and output folder for pdfs
        input_txt_folder_path = config.get("extracted_txt")# Specify the folder path
        outpt_txt_folder_path = config.get("final_ext_txt")# Specify the folder path
    else:
        print("Error loading config file!")
        # Handle the error gracefully, e.g., exit or provide a default value

    section_formatter(input_txt_folder_path, outpt_txt_folder_path)