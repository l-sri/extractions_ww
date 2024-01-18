import typing
import os
import IPython.display
from PIL import Image as PIL_Image
from PIL import ImageOps as PIL_ImageOps
from typing import Union
from vertexai.preview.generative_models import (
    GenerationConfig,
    GenerativeModel,
    Image,
    Part,
)

def display_images(
    images: typing.Iterable[Image],
    max_width: int = 600,
    max_height: int = 350,
) -> None:
    for image in images:
        pil_image = typing.cast(PIL_Image.Image, image._pil_image)
        if pil_image.mode != "RGB":
            # RGB is supported by all Jupyter environments (e.g. RGBA is not yet)
            pil_image = pil_image.convert("RGB")
        image_width, image_height = pil_image.size
        if max_width < image_width or max_height < image_height:
            # Resize to display a smaller notebook image
            pil_image = PIL_ImageOps.contain(pil_image, (max_width, max_height))
        IPython.display.display(pil_image)


def get_image_bytes_from_file(filepath: str) -> bytes:
    with open(filepath, "rb") as f:
        image_bytes = f.read()
    return image_bytes


def load_image_from_file(image_bytes: str) -> Image:
    image_bytes = get_image_bytes_from_file(image_bytes)
    return Image.from_bytes(image_bytes)


def display_content_as_image(content: Union[str, Image, Part]) -> bool:
    if not isinstance(content, Image):
        return False
    display_images([content])
    return True


def display_content_as_video(content: Union[str, Image, Part]) -> bool:
    if not isinstance(content, Part):
        return False
    part = typing.cast(Part, content)
    file_path = part.file_data.file_uri.removeprefix("gs://")
    video_url = f"https://storage.googleapis.com/{file_path}"
    IPython.display.display(IPython.display.Video(video_url, width=600))
    return True


def print_multimodal_prompt(contents: list[Union[str, Image, Part]]):
    """
    Given contents that would be sent to Gemini,
    output the full multimodal prompt for ease of readability.
    """
    for content in contents:
        if display_content_as_image(content):
            continue
        if display_content_as_video(content):
            continue
        print(content)


multimodal_model = GenerativeModel("gemini-pro-vision")

generation_config = GenerationConfig(
    temperature=0.01,
    top_p=0.8,
    top_k=10,
    candidate_count=1,
    max_output_tokens=2048,
)


image_folder_path = "data/imagefiles"
output_folder_path = "/mnt/resources/woolworths/extracted_infographics_txt"

for folder_name in os.listdir(image_folder_path):
    folder_path = os.path.join(image_folder_path, folder_name)
    if os.path.isdir(folder_path):
        image_files = [
            f for f in os.listdir(folder_path) if f.endswith((".jpg", ".png", ".bmp"))
        ]
        image_files = sorted(image_files)

        result_string = ""
        number = 1
        for image_file in image_files:
            image_path = os.path.join(folder_path, image_file)
            image = load_image_from_file(image_path)

            instructions = """Instructions: Consider the following image that has exactly one of the following two formats:
                            Type 1) It contains a routine where the X-axis has time and the Y-axis has sections that contain tasks. There are a lot of tasks written here which can be mapped to a time period from the X-axis. Map these tasks to a start time and an end time.
                            Type 2) It contains text with some tables. All text from the tables needs to be extracted accurately."""
            prompt1 = """
            Do the following steps:
            1. Check if the content inside the image is of format `Type 1` or format `Type 2`. Make sure you look at each and every part of the image for information.
            2. If the image is of format `Type 1`, include all tasks mentioned there along with the start time and end time for the corresponding task. Be specific and make sure you don't miss anything.
            If the image is of format `Type 2`, extract it fully and include all text including any titles if applicable. Be specific and make sure you don't miss anything.
            3. Please double check your work and make sure all text is being extracted.
            """

            contents = [
                instructions,
                image,
                prompt1,
            ]

            responses = multimodal_model.generate_content(contents, stream=True, generation_config= generation_config)

            # print("-------Prompt--------")
            # print_multimodal_prompt(contents)

            # print("\n-------Response--------")
            if number == 1:
                result_string += ""
            else:
                result_string += "\n\n"
            result_string += "Page Number: {}".format(number) + "\n\n"
            for response in responses:
                result_string += response.text
            number+=1

        print(result_string)

        output_file_path = os.path.join(output_folder_path, f"{folder_name}.txt")
        with open(output_file_path, "w") as f:
            f.write(result_string)