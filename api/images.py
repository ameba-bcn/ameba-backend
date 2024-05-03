import re
import base64
import mimetypes
from PIL import Image as PilImage
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile


def match_base64_format(data: str) -> bool:
    pattern = r'data:image/(?P<format>[a-zA-Z]+);base64,(?P<data>.+)'
    return re.match(pattern, data)


def decode_base64_image(image_data: str) -> ContentFile:
    match = match_base64_format(image_data)
    if not match:
        raise ValueError("Invalid data format")
    ext = match.group('format')
    data = match.group('data')
    data = base64.b64decode(data)
    return ContentFile(data), ext

def exists_image(image: ContentFile) -> bool:
    try:
        img = PilImage.open(image)
        return True
    except Exception:
        return False

def is_valid_image(
        image: ContentFile, max_size=(1920, 1080), img_format='JPEG'
) -> bool:
    if not exists_image(image):
        return True
    img = PilImage.open(image)
    if (
            img.size[0] <= max_size[0]
            and img.size[1] <= max_size[1]
            and img.format.lower() == img_format.lower()
    ):
        return True
    return False

def adjust_image_orientation(img):
    try:
        exif = img._getexif()
        orientation_key = 274  # cf ExifTags
        if exif and orientation_key in exif:
            orientation = exif[orientation_key]
            if orientation == 3:
                img = img.rotate(180, expand=True)
            elif orientation == 6:
                img = img.rotate(270, expand=True)
            elif orientation == 8:
                img = img.rotate(90, expand=True)
    except AttributeError:
        # No EXIF metadata present
        pass
    return img


def resize_image(image: ContentFile, max_size=(1920, 1080), img_format='JPEG') -> InMemoryUploadedFile:
    img = PilImage.open(image)
    img = adjust_image_orientation(img)
    if (
            img.size[0] <= max_size[0]
            and img.size[1] <= max_size[1]
            and img.format.lower() == img_format.lower()
    ):
        return image

    # Convert image to RGB to ensure compatibility with JPEG
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')

    # Resize the image
    img.thumbnail(max_size, PilImage.ANTIALIAS)

    # Save the image to a BytesIO object
    img_io = BytesIO()
    img.save(img_io, format=img_format, quality=70)  # Adjust quality as needed

    # Create a new Django file-like object
    new_image = InMemoryUploadedFile(
        img_io, 'ImageField', f"{image.name.split('.')[0]}.{img_format.lower()}",
        f'image/{img_format.lower()}', img_io.getbuffer().nbytes, None
    )
    return new_image


def replace_image_field(image_field):
    """ Function that receives a django ImageField and replaces the image with
    a resized version removing the original one.
    """
    image = image_field
    if not is_valid_image(image):
        new_image = resize_image(image)
        image_field.delete(save=False)
        image_field.save(new_image.name, new_image, save=False)
    return image_field


def get_base64_image(image_field):
    # Ensure there is an image in the ImageField
    if not image_field:
        return None

    # Get the MIME type of the file based on its extension
    mime_type, _ = mimetypes.guess_type(image_field.name)
    if not mime_type:
        mime_type = 'application/octet-stream'  # Use a binary data type if MIME type is unknown

    # Read the image file
    if image_field.file.multiple_chunks():
        content = b''.join(chunk for chunk in image_field.file.chunks())
    else:
        content = image_field.file.read()

    # Encode the image content in base64
    image_base64 = base64.b64encode(content)

    # Convert bytes to string and prepend the data URI prefix
    image_base64_str = f"data:{mime_type};base64,{image_base64.decode('utf-8')}"

    # Return the base64 string with prefix
    return image_base64_str
