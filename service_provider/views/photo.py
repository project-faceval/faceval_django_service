import http.client
from collections import defaultdict

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.db import transaction, models
from django.contrib.auth.models import User

from service_provider.rest.handlers import RestRequestHandler
from service_provider.models import PhotoBlog, Profile
from service_provider.forms import PhotoBlogForm, PhotoUpdateForm, PhotoValidationForm, PhotoDeleteForm
from service_provider.utils import save_image, get_photo_info, optional_update, remove_image


class PhotoBlogViewSet(RestRequestHandler):
    @csrf_exempt
    def rest_view(self, request, *args, **kwargs):
        return super().rest_view(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        photo_id = request.GET.get("id")
        user_id = request.GET.get("user_id")

        if photo_id is None and user_id is None:
            return HttpResponse(status=http.client.BAD_REQUEST)

        if photo_id is not None:
            return JsonResponse(get_photo_info(PhotoBlog.objects.exclude(tag__regex=r'^.*D.*$')
                                                                .get(id=photo_id)), safe=False)
        else:
            try:
                profile = Profile.objects.get(user=User.objects.get(username=user_id))
            except User.DoesNotExist or Profile.DoesNotExist:
                return HttpResponse(status=http.client.NOT_FOUND)
            else:
                return JsonResponse([*get_photo_info(PhotoBlog.objects
                                                              .filter(user=profile)
                                                              .exclude(tag__regex=r'^.*D.*$')
                                                              .all())], safe=False)

    def post(self, request, *args, **kwargs):
        form = PhotoBlogForm(request.POST, request.FILES)
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
            file_name = save_image(form.cleaned_data['image'], form.cleaned_data['ext'])
            try:
                new_blog = PhotoBlog.objects.create(user=profile,
                                                    score=form.cleaned_data.get('score'),
                                                    face_positions=form.cleaned_data['positions'],
                                                    title=form.cleaned_data.get('title'),
                                                    description=form.cleaned_data.get('description'),
                                                    path=file_name)
                new_blog.save()
            except Exception as e:
                remove_image(file_name)
                raise e

        return JsonResponse(get_photo_info(new_blog), safe=False, status=http.client.CREATED)

    def put(self, request, *args, **kwargs):
        form = PhotoUpdateForm(request.GET)
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
        return JsonResponse(get_photo_info(blog), safe=False)

    def delete(self, request, *args, **kwargs):
        form = PhotoDeleteForm(request.GET)
        if not form.is_valid():
            return HttpResponse(status=http.client.BAD_REQUEST)

        user = form.authenticate()
        if user is None:
            return HttpResponse(status=http.client.UNAUTHORIZED)

        blog = PhotoBlog.objects.get(id=form.cleaned_data['photo_id'])

        if not user.is_superuser and blog.user != user:
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
