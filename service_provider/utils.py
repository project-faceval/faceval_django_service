from typing import Iterable
import json

from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
import uuid
from pathlib import Path
import os
from PIL import Image
from io import BytesIO
import base64


class ModelEncoderAdapter(DjangoJSONEncoder):

    def default(self, o):
        if isinstance(o, models.Model):
            return serialize("json", dict(o))

        return serialize("json", o)


def get_user_info(profile, user):
    return {
        "id": user.username,
        "email": user.email,
        "display_name": profile.display_name,
        "gender": profile.gender,
        "status": profile.status,
        "date_added": user.date_joined,
    }


def get_photo_info(photo, attach_base=False):
    if not isinstance(photo, Iterable):
        photo = [photo]

    for p in photo:
        yield {
            "id": p.id,
            "base": p.image if attach_base else "",
            "score": p.score,
            "positions": p.face_positions,
            "title": p.title,
            "description": p.description,
            "date_added": p.date_added,
            "tag": p.tag,
        }


def optional_update(old_data, new_data, keep_pattern="||%%USE_PREVIOUS%%||",
                    keep_if_none=True,
                    empty_str_to_none=False,
                    skip_empty_str=False,
                    strip_string=False):
    if strip_string and isinstance(new_data, str):
        new_data = new_data.strip()

    if new_data == keep_pattern or (keep_if_none and new_data is None):
        return old_data

    if skip_empty_str and new_data == "":
        return old_data

    if empty_str_to_none and new_data == "":
        return None

    return new_data


# image_path = Path(os.path.dirname(__file__)).parent.resolve() / 'static' / 'images'
image_path = Path('/tmp') / 'faceval' / 'images'


def get_uuid():
    return str(uuid.uuid1())


def save_image(multipart_file, ext):
    file_name = f"{get_uuid()}.{ext}"
    path = image_path / file_name

    if not image_path.exists():
        os.makedirs(image_path)

    with open(path, 'wb+') as f:
        for chunk in multipart_file.chunks():
            f.write(chunk)

    return path


def remove_image(file_name):
    os.remove(image_path / file_name)


size = 300


def encode_image(multipart_file, ext, compress: bool):
    path = save_image(multipart_file, ext)

    image = Image.open(path)

    if compress:
        width = image.size[0]
        height = image.size[1]

        if width > height:
            new_height = 300
            new_width = int(300 * width / height)
        else:
            new_width = 300
            new_height = int(300 * height / width)

        image = image.resize((new_width, new_height))

    buffer = BytesIO()
    image.save(buffer, format=ext)

    base64_code = base64.b64encode(buffer.getvalue())

    image.close()
    os.remove(path)

    return str(base64_code)


def json_request_compat(request, method="GET"):
    if request.content_type == 'application/json':
        return json.loads(request.body)

    if method == "POST":
        return request.POST
    else:
        return request.GET
