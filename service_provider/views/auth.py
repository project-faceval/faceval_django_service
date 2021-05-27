import http.client

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from service_provider.rest.handlers import RestRequestHandler, HttpResponse
from service_provider import forms


class AuthenticationViewSet(RestRequestHandler):
    @csrf_exempt
    def rest_view(self, request, *args, **kwargs):
        return super().rest_view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = forms.UserAuthenticationForm(request.POST)
        if not form.is_valid():
            return HttpResponse(status=http.client.BAD_REQUEST)

        user = form.authenticate()
        if user is None:
            return HttpResponse(status=http.client.UNAUTHORIZED)

        return JsonResponse({"status": "OK"}, status=http.client.OK)
