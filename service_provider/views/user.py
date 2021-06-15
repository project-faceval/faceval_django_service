import http.client

from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.models import User
import json

from service_provider.rest.handlers import RestRequestHandler, HttpResponse
from service_provider.models import Profile
from service_provider import forms
from service_provider.utils import get_user_info, optional_update


class UserInfoViewSet(RestRequestHandler):

    @csrf_exempt
    def rest_view(self, request, *args, **kwargs):
        return super().rest_view(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        key_id = request.GET.get('id')

        if key_id is None:
            return HttpResponse(status=http.client.BAD_REQUEST)
        else:
            pure_id = str(key_id).strip()

            if pure_id == '':
                return HttpResponse(status=http.client.BAD_REQUEST)
            else:
                try:
                    user = User.objects.get(username=pure_id)
                    profile = Profile.objects.get(user=user)
                except User.DoesNotExist or Profile.DoesNotExist:
                    return HttpResponse(status=http.client.NOT_FOUND)

                return JsonResponse(get_user_info(profile, user), safe=False)

    def post(self, request, *args, **kwargs):
        if request.content_type == 'application/json':
            form = forms.MinimalUserForm(json.loads(request.body))
        else:
            form = forms.MinimalUserForm(request.POST)
        if not form.is_valid():
            return HttpResponse(status=http.client.BAD_REQUEST)

        with transaction.atomic():
            new_user = User.objects.create_user(form.cleaned_data['id'],
                                                form.cleaned_data['email'],
                                                form.cleaned_data['password'])
            profile = Profile.objects.create(user=new_user,
                                             display_name=form.cleaned_data['display_name'])

        return JsonResponse(get_user_info(profile, new_user), safe=False, status=http.client.CREATED)

    def put(self, request, *args, **kwargs):
        if request.content_type == 'application/json':
            form = forms.FullUserForm(json.loads(request.body))
        else:
            form = forms.FullUserForm(request.GET)
        if not form.is_valid():
            return HttpResponse(status=http.client.BAD_REQUEST)

        user = form.authenticate()
        if user is None:
            return HttpResponse(status=http.client.UNAUTHORIZED)

        try:
            user_profile = Profile.objects.get(user__username=user.username)
        except Profile.DoesNotExist:
            return HttpResponse(status=http.client.NOT_FOUND)

        user.email = optional_update(user.email, form.cleaned_data.get('email'),
                                     skip_empty_str=True,
                                     strip_string=True,
                                     empty_str_to_none=False,
                                     keep_if_none=True)
        user_profile.display_name = optional_update(user_profile.display_name, form.cleaned_data.get('display_name'),
                                                    skip_empty_str=True)

        user_profile.gender = optional_update(user_profile.gender, bool(form.cleaned_data.get('gender')),
                                              empty_str_to_none=True)
        user_profile.status = optional_update(user_profile.status, form.cleaned_data.get('status'),
                                              empty_str_to_none=True)

        with transaction.atomic():
            user.save()
            user_profile.save()

        return JsonResponse(get_user_info(user_profile, user), safe=False, status=http.client.OK)

    def delete(self, request, *args, **kwargs):
        form = forms.UserAuthenticationForm(request.GET)
        if not form.is_valid():
            return HttpResponse(status=http.client.BAD_REQUEST)

        user = form.authenticate()
        if user is None:
            return HttpResponse(status=http.client.UNAUTHORIZED)

        user.delete()
        return JsonResponse({"id": user.username}, safe=False, status=http.client.OK)

    def patch(self, request, *args, **kwargs):
        form = forms.PasswordChangeForm(request.GET)
        if not form.is_valid():
            return HttpResponse(status=http.client.BAD_REQUEST)

        user = form.authenticate()
        if user is None:
            return HttpResponse(status=http.client.UNAUTHORIZED)

        user.set_password(form.cleaned_data['new_password'])
        user.save()

        return JsonResponse({"status": "OK"}, safe=False, status=http.client.OK)
