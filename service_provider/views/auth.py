import http.client

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

from service_provider.rest.handlers import RestRequestHandler, HttpResponse
from service_provider import forms
from service_provider.utils import json_request_compat


class AuthenticationViewSet(RestRequestHandler):
    @csrf_exempt
    def rest_view(self, request, *args, **kwargs):
        return super().rest_view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        params = json_request_compat(request, method='POST')

        form = forms.UserAuthenticationForm(params)
        if not form.is_valid():
            return HttpResponse(status=http.client.BAD_REQUEST)

        user = form.authenticate()
        if user is None:
            return HttpResponse(status=http.client.UNAUTHORIZED)

        return JsonResponse({"status": "OK"}, status=http.client.OK)
