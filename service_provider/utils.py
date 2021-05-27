from typing import Iterable

from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
import uuid
from pathlib import Path
import os


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


def get_photo_info(photo):
    if not isinstance(photo, Iterable):
        photo = [photo]

    info = []

    for p in photo:
        info.append({
            "id": p.id,
            "path": p.path,
            "score": p.score,
            "face_positions": p.face_positions,
            "title": p.title,
            "description": p.description,
            "date_added": p.date_added,
            "tag": p.tag,
        })

    size = len(info)

    if size <= 0:
        return None
    elif size == 1:
        return info[0]
    else:
        return info


def optional_update(old_data, new_data, keep_pattern="||%%KEEP_FORMAL%%||",
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


image_path = Path(os.path.dirname(__file__)).parent.resolve() / 'static' / 'images'


def get_uuid():
    return str(uuid.uuid1())


def save_image(multipart_file, ext):
    file_name = f"{get_uuid()}.{ext}"
    path = image_path / file_name

    with open(path, 'wb+') as f:
        for chunk in multipart_file.chunks():
            f.write(chunk)

    return file_name


def remove_image(file_name):
    os.remove(image_path / file_name)
