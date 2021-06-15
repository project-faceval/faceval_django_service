from django.apps import AppConfig

from py_eureka_client import eureka_client


ZONES = {
    "defaultZone": "http://127.0.0.1:9237/eureka",
    # "nanjing-1": "http://127.0.0.1:9237/eureka",
}

ZONE = "defaultZone"
# ZONE = "nanjing-1"

SERVICE_NAME = 'fv-service'


def get_ip() -> str:
    return '127.0.0.1'


def get_port() -> int:
    return 8729


class ServiceProviderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'service_provider'

    verbose_name = 'FACEVAL Service Provider using Django'
    default = True

    def ready(self):
        eureka_client.init(eureka_availability_zones=ZONES, zone=ZONE,
                           app_name=SERVICE_NAME,
                           instance_ip=get_ip(),
                           instance_port=get_port())
