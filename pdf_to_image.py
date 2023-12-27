from pdf2image import convert_from_path
import os

def file_to_image(input_file, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Convert the PDF to individual images
    images = convert_from_path(input_file)

    # Enumerate and save each image
    for i, page in enumerate(images):
        # Generate unique filenames based on page number
        filename = f"{output_dir}/page_{i+1}.jpg"
        # Save the image with the chosen format (JPG in this case)
        page.save(filename, "JPEG")

    print(f"Successfully converted PDF to images in {output_dir}")

input_file = "data/input/Markdown_Protocols.pdf"
output_dir = "data/imagefiles/Markdown_Protocols"

file_to_image(input_file, output_dir)