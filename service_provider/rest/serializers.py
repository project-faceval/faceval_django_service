from abc import abstractmethod

from django.core import serializers


class ModelMapper(object):
    model_type = None

    @abstractmethod
    def serialize(self, model_dict: dict) -> model_type:
        pass

    @abstractmethod
    def deserialize(self, model: model_type) -> dict:
        pass


def serialize(data, serializer="django"):
    return serializers.serialize("json", data)


def deserialize(json_str, serializer="django"):
    return serializers.deserialize("json", json_str)
