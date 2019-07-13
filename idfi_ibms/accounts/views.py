from __future__ import unicode_literals
from generic.response.http import StandardHttpResponse
from generic.misc.oauth_provider import TokenView
from generic.misc.authentication import hasValidAuthHeaderMobile
from generic.feature.users.user_utils import UserUtils
from generic.database.users import UserModelQueries
from generic.misc.timezone import utc
from idfi_ibms.settings import REDIRECT_URL
from django.contrib.auth import authenticate
from django.contrib.auth import logout
from rest_framework.views import APIView
from oauth2_provider.models import AccessToken, Application
from datetime import datetime
import json
import urllib
import random
import string
import base64

def get_application_token():
    try:
        application_obj = Application.objects.get(name='idfi_ibms')
    except Application.DoesNotExist:
        return False
    client_str = application_obj.client_id + ':' + application_obj.client_secret
    authorization_string = base64.b64encode(client_str.encode())
    return authorization_string


def delete_other_token(user_id):
    token_obj_list = AccessToken.objects.filter(user_id=user_id)
    for token_obj in token_obj_list:
        token_obj.delete()

'''
class Login(APIView):

    @staticmethod
    def post(request):
        """
		Authenticate user.
		:param request:
		:return:
        """
        try:
            json_body = request.data.copy()
            request._body = urllib.parse.urlencode(json_body)
            #json_body['redirect_uri'] = REDIRECT_URL
            #request._post = json_body
        except Exception as e:
            return StandardHttpResponse.bad_rsp([], e.__str__())

        view = TokenView.as_view()
        username = json_body["username"] if "username" in json_body else False
        password = json_body["password"] if "password" in json_body else False

        if not username or not password:
            return StandardHttpResponse.login_bad_rsp([], 'Credentials missing')
        user = authenticate(username=username, password=password)
        if not user:
            return StandardHttpResponse.login_bad_rsp([], 'Wrong credentials')

        application_token = get_application_token()
        if not application_token:
            return StandardHttpResponse.bad_rsp([], 'Application is not ready. Please contact Admin.')

        delete_other_token(user.id)
        request.META["HTTP_AUTHORIZATION"] = "Basic " + application_token.decode()
        request.META["CONTENT_TYPE"] = "application/x-www-form-urlencoded"
        data={"HTTP_AUTHORIZATION":request.META["HTTP_AUTHORIZATION"]}
        return StandardHttpResponse.login_rsp(data, 'User Logged-In Successfully.')'''

def login(request):
        """
        Authenticate user.
        :param request:
        :return:
        """
        try:
            json_body = json.loads(request.body)
            request._body = urllib.parse.urlencode(json_body)
            json_body['redirect_uri'] = REDIRECT_URL
            request._post = json_body
        except Exception as e:
            return StandardHttpResponse.bad_rsp([], e.__str__())

        view = TokenView.as_view()
        username = json_body["username"] if "username" in json_body else False
        password = json_body["password"] if "password" in json_body else False

        if not username or not password:
            return StandardHttpResponse.login_bad_rsp([], 'Credentials missing')
        user = authenticate(username=username, password=password)
        if not user:
            return StandardHttpResponse.login_bad_rsp([], 'Wrong credentials')

        application_token = get_application_token()
        if not application_token:
            return StandardHttpResponse.bad_rsp([], 'Application is not ready. Please contact Admin.')
        delete_other_token(user.id)
        request.META["HTTP_AUTHORIZATION"] = "Basic " + application_token.decode()
        request.META["CONTENT_TYPE"] = "application/x-www-form-urlencoded"
        return StandardHttpResponse.login_rsp(json.loads(view(request).content), 'User Logged-In Successfully.')


class Logout(APIView):

    permission_classes = (hasValidAuthHeaderMobile,)

    @staticmethod
    def post(request):
        """
        To logout a user means to expire the oauth token
        :param request:
        :return:
        """
        logout(request)
        token = request.token
        token_obj = AccessToken.objects.get(token=token)
        token_obj.expires = datetime.now(utc)
        token_obj.save()
        return StandardHttpResponse.rsp_200([], 'Logout Successfully.')


def create_random_password(length=8):
    password = ''.join(random.choice(string.digits + string.uppercase + string.lowercase + '@!#$&')
                       for tmp in range(length))
    return password

