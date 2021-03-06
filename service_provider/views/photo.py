import http.client
from collections import defaultdict
import json

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.db import transaction, models
from django.contrib.auth.models import User

from service_provider.rest.handlers import RestRequestHandler
from service_provider.models import PhotoBlog, Profile
from service_provider.forms import PhotoBlogForm, PhotoBlogFormBase64, PhotoUpdateForm, PhotoValidationForm,\
                                    PhotoDeleteForm
from service_provider.utils import save_image, get_photo_info, optional_update,\
                                    remove_image, encode_image, json_request_compat


def get_attach_base(request):
    attach_base = request.GET.get("attach_base")
    return True if attach_base is not None and str(attach_base).lower() == 'true' else False


def get_save_thumbnail(request):
    ut = request.GET.get("save_thumbnail")
    return True if ut is not None and str(ut).lower() == 'true' else False


class PhotoBlogViewSet(RestRequestHandler):
    @csrf_exempt
    def rest_view(self, request, *args, **kwargs):
        return super().rest_view(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        photo_id = request.GET.get("id")
        user_id = request.GET.get("user_id")

        attach_base = get_attach_base(request)

        if photo_id is None and user_id is None:
            return HttpResponse(status=http.client.BAD_REQUEST)

        if photo_id is not None:
            try:
                return JsonResponse([*get_photo_info(PhotoBlog.objects.exclude(tag__regex=r'^.*D.*$')
                                                                      .get(id=photo_id), attach_base)], safe=False)
            except PhotoBlog.DoesNotExist:
                return HttpResponse(status=http.client.NOT_FOUND)
        else:
            try:
                profile = Profile.objects.get(user=User.objects.get(username=user_id))
            except User.DoesNotExist or Profile.DoesNotExist:
                return HttpResponse(status=http.client.NOT_FOUND)
            else:
                return JsonResponse([*get_photo_info(PhotoBlog.objects
                                                              .filter(user=profile)
                                                              .exclude(tag__regex=r'^.*D.*$')
                                                              .all(), attach_base)], safe=False)

    def post(self, request, *args, **kwargs):
        params = json_request_compat(request, method='POST')

        use_base64 = params.get("use_base64")
        use_base64 = use_base64 is not None and use_base64 == 'yes'

        attach_base = get_attach_base(request)
        save_thumbnail = get_save_thumbnail(request)

        if use_base64:
            form = PhotoBlogFormBase64(params)
        else:
            form = PhotoBlogForm(params, request.FILES)

        if not form.is_valid():
            return HttpResponse(status=http.client.BAD_REQUEST)

        user = form.authenticate()
        if user is None:
            return HttpResponse(status=http.client.UNAUTHORIZED)

        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            return HttpResponse(status=http.client.FORBIDDEN)

        with transaction.atomic():
            if use_base64:
                base64_code = form.cleaned_data['image']
            else:
                base64_code = encode_image(form.cleaned_data['image'], form.cleaned_data['ext'], save_thumbnail)
            new_blog = PhotoBlog.objects.create(user=profile,
                                                score=form.cleaned_data.get('score'),
                                                face_positions=form.cleaned_data['positions'],
                                                title=form.cleaned_data.get('title'),
                                                description=form.cleaned_data.get('description'),
                                                path="",
                                                image=base64_code)
            new_blog.save()

        return JsonResponse([*get_photo_info(new_blog, attach_base)][0], safe=False, status=http.client.CREATED)

    def put(self, request, *args, **kwargs):
        params = json_request_compat(request)

        attach_base = get_attach_base(request)

        form = PhotoUpdateForm(params)
        if not form.is_valid():
            return HttpResponse(status=http.client.BAD_REQUEST)

        user = form.authenticate()
        if user is None:
            return HttpResponse(status=http.client.UNAUTHORIZED)

        blog = PhotoBlog.objects.get(id=form.cleaned_data['photo_id'])
        blog.title = optional_update(blog.title, form.cleaned_data.get('title'),
                                     empty_str_to_none=True,
                                     keep_if_none=True,
                                     strip_string=True,
                                     skip_empty_str=False)
        blog.score = optional_update(blog.score, form.cleaned_data.get('score'),
                                     keep_if_none=True)
        blog.description = optional_update(blog.description, form.cleaned_data.get('description'),
                                           skip_empty_str=False,
                                           empty_str_to_none=True,
                                           keep_if_none=True,
                                           strip_string=False)

        blog.save()
        return JsonResponse([*get_photo_info(blog, attach_base)][0], safe=False)

    def delete(self, request, *args, **kwargs):
        params = request.GET

        form = PhotoDeleteForm(params)
        if not form.is_valid():
            return HttpResponse(status=http.client.BAD_REQUEST)

        user = form.authenticate()
        if user is None:
            return HttpResponse(status=http.client.UNAUTHORIZED)

        blog = PhotoBlog.objects.get(id=form.cleaned_data['photo_id'])

        if not user.is_superuser and blog.user.user.id != user.id:
            return HttpResponse(status=http.client.FORBIDDEN)

        fake_delete = not user.is_superuser or form.cleaned_data.get('fake_delete')

        if fake_delete:
            if blog.tag is None:
                blog.tag = "D"
            elif "D" not in blog.tag:
                blog.tag += "D"

            blog.save()
        else:
            blog.delete()

        return JsonResponse({"id": form.cleaned_data['id'], "fake_delete": fake_delete}, safe=False)
