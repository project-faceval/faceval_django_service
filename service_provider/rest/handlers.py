import http.client

from django.http import HttpResponse, JsonResponse


GET = "GET"
POST = "POST"
PUT = "PUT"
DELETE = "DELETE"
PATCH = "PATCH"


class RestRequestHandler(object):
    def __init__(self, get_view=None, post_view=None, put_view=None, delete_view=None, patch_view=None):
        self.views = {
            GET: self.get,
            POST: self.post,
            PUT: self.put,
            DELETE: self.delete,
            PATCH: self.patch,
        }

        alter_views = {
            GET: get_view,
            POST: post_view,
            PUT: put_view,
            DELETE: delete_view,
            PATCH: patch_view,
        }

        for key, val in alter_views.items():
            if val is not None:
                self.views[key] = val

        del alter_views

    @property
    def method_not_allowed(self):
        return HttpResponse(status=http.client.METHOD_NOT_ALLOWED)

    @property
    def bad_request(self):
        return HttpResponse(status=http.client.BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        return self.method_not_allowed

    def post(self, request, *args, **kwargs):
        return self.method_not_allowed

    def put(self, request, *args, **kwargs):
        return self.method_not_allowed

    def delete(self, request, *args, **kwargs):
        return self.method_not_allowed

    def patch(self, request, *args, **kwargs):
        return self.method_not_allowed

    def rest_view(self, request, *args, **kwargs):
        try:
            return self.views[request.method](request, *args, **kwargs)
        except KeyError:
            return self.bad_request


def wrap_json_response(response):
    if response is not HttpResponse:
        response = JsonResponse(response, safe=False)

    return response


class JsonResponseRestRequestHandler(RestRequestHandler):
    def method_not_allowed(self):
        return JsonResponse({}, status=http.client.METHOD_NOT_ALLOWED)

    def bad_request(self):
        return JsonResponse({}, status=http.client.BAD_REQUEST)

    @staticmethod
    def created(response):
        return JsonResponse(response, status=http.client.CREATED)

    def rest_view(self, request, *args, **kwargs):
        return wrap_json_response(super().rest_view(request, *args, **kwargs))
