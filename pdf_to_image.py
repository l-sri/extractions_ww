from pdf2image import convert_from_path
import os

def file_to_image(input_file, output_dir):
    """Converts a PDF file to images and saves them in the specified output directory."""

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    images = convert_from_path(input_file)

    for i, page in enumerate(images):
        filename = f"{output_dir}/page_{i+1}.jpg"
        page.save(filename, "JPEG")

    print(f"Successfully converted PDF '{input_file}' to images in {output_dir}")

# Specify the input directory
input_dir = "/mnt/resources/woolworths/raw_infographics"

# Iterate through all PDF files in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith(".pdf"):
        input_file = os.path.join(input_dir, filename)
        output_dir = os.path.join("data/imagefiles", os.path.splitext(filename)[0])  # Generate output directory based on filename
        file_to_image(input_file, output_dir)