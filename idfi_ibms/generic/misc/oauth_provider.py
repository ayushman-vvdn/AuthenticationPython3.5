from __future__ import unicode_literals

import json
#import urlparse
import urllib.parse as urlparse

from braces.views import CsrfExemptMixin
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import View
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.views.mixins import OAuthLibMixin

from generic.feature.users.user_login import real_login_helper_token


class TokenView(CsrfExemptMixin, OAuthLibMixin, View):
    """
    Implements an endpoint to provide access tokens

    The endpoint is used in the following flows:
    * Authorization code
    * Password
    * Client credentials
    """
    server_class = oauth2_settings.OAUTH2_SERVER_CLASS
    validator_class = oauth2_settings.OAUTH2_VALIDATOR_CLASS
    oauthlib_backend_class = oauth2_settings.OAUTH2_BACKEND_CLASS

    @method_decorator(sensitive_post_parameters('password'))
    def post(self, request, *args, **kwargs):

        password = urlparse.parse_qs(request.body)["password"][0]
        if not password:
            return HttpResponse(content=json.dumps({"err": "password is missing"}), status=400)
        l_data = {}
        url, headers, body, status = self.create_token_response(request)
        if status is 200:
            body = json.loads(body)
            l_bool, l_data = real_login_helper_token(body["access_token"])
            l_data["credentials"] = body
            if not l_bool:
                response = HttpResponse(content=json.dumps(l_data), status=400)
            else:
                response = HttpResponse(content=json.dumps(l_data), status=status)
        else:
            response = HttpResponse(content=body, status=status)

        for k, v in headers.items():
            response[k] = v
        return response
