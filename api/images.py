import re
import base64
from PIL import Image as PilImage
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile


def decode_base64_image(image_data: str) -> ContentFile:
    pattern = r'data:image/(?P<format>[a-zA-Z]+);base64,(?P<data>.+)'
    match = re.match(pattern, image_data)
    if not match:
        raise ValueError("Invalid data format")
    ext = match.group('format')
    data = match.group('data')
    data = base64.b64decode(data)
    return ContentFile(data), ext


def resize_image(image: ContentFile, max_size=(1920, 1080), format='JPEG') -> InMemoryUploadedFile:
    img = PilImage.open(image)

    # Convert image to RGB to ensure compatibility with JPEG
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')

    # Resize the image
    img.thumbnail(max_size, PilImage.ANTIALIAS)

    # Save the image to a BytesIO object
    img_io = BytesIO()
    img.save(img_io, format=format, quality=90)  # Adjust quality as needed

    # Create a new Django file-like object
    new_image = InMemoryUploadedFile(
        img_io, 'ImageField', f"{image.name.split('.')[0]}.{format.lower()}",
        f'image/{format.lower()}', img_io.getbuffer().nbytes, None
    )
    return new_image


def replace_image_field(image_field):
    """ Function that receives a django ImageField and replaces the image with
    a resized version removing the original one.
    """
    image = image_field
    new_image = resize_image(image)
    image_field.delete(save=False)
    image_field.save(new_image.name, new_image, save=False)
    return image_field
