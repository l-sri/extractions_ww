import typing
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

toc_image_path = "data/imagefiles/Markdown_Protocols/page_1.jpg"
toc_image = load_image_from_file(toc_image_path)



instructions = "Instructions: Consider the following image that contains a table of contents:"
prompt1 = """
Carefully look at this image and display the table of contents from this image in an easy to read format.
Make sure you match section name with it's corresponding page number.
"""


contents = [
    instructions,
    toc_image,
    prompt1,
]

responses = multimodal_model.generate_content(contents, stream=True, generation_config= generation_config)

# print("-------Prompt--------")
# print_multimodal_prompt(contents)

# print("\n-------Response--------")
for response in responses:
    print(response.text , end="")