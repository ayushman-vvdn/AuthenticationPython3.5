from __future__ import unicode_literals
from oauth2_provider.models import AccessToken
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _
from generic.database.users import UserModelQueries
import json


def get_user_profile(user):
    return UserModelQueries.get_user_profile_by_user_id(user.id)


class hasValidAuthHeader(BaseAuthentication):
    """
    Token based authentication using the OAUTH Token standard.
    TODO :: Write the test cases here.
    """

    def has_permission(self, request, view):

        if type(request.data) == dict:
            request.body = str(json.dumps(request.data))
        two_tuple = self.authenticate_user(request)
        if not two_tuple:
            return False
        user = two_tuple[0]
        val = two_tuple[1]

        user_profile = get_user_profile(user)
        if not user_profile:
            return False

        if user and user_profile.is_active:
            request.user = user
            request.profile = user_profile
            request.token = val
            return True
        else:
            return False

    def authenticate_user(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using OAUTH-based authentication.  Otherwise returns `None`.
        """
        oauth_value = self.get_oauth_value(request)
        if oauth_value is None:
            return None

        try:
            access_token = AccessToken.objects.get(token=oauth_value)
            if access_token.is_expired():
                request.authenticators = False
                return None
        except AccessToken.DoesNotExist:
            request.authenticators = False
            return None

        return access_token.user, oauth_value

    def get_oauth_value(self, request):
        auth = get_authorization_header(request).split()
        auth_header_prefix = "bearer"

        if not auth or smart_text(auth[0].lower()) != auth_header_prefix:
            return None

        if len(auth) == 1:
            msg = _('Invalid Authorization header. No credentials provided.')
            raise exceptions.PermissionDenied(msg)
        elif len(auth) > 2:
            msg = _('Invalid Authorization header. Credentials string '
                    'should not contain spaces.')
            raise exceptions.PermissionDenied(msg)

        return auth[1]


class hasValidAuthHeaderMobile(BaseAuthentication):
    """
    Token based authentication using the OAUTH Token standard.
    TODO :: Write the test cases here.
    """

    def has_permission(self, request, view):

        if type(request.data) == dict:
            request.body = str(json.dumps(request.data))
        two_tuple = self.authenticate_user(request)
        if not two_tuple:
            return False
        user = two_tuple[0]
        val = two_tuple[1]

        user_profile = get_user_profile(user)
        if not user_profile:
            return False

        if user:
            request.user = user
            request.profile = user_profile
            request.token = val
            return True
        else:
            return False

    def authenticate_user(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using OAUTH-based authentication.  Otherwise returns `None`.
        """
        oauth_value = self.get_oauth_value(request)
        if oauth_value is None:
            return None

        try:
            access_token = AccessToken.objects.get(token=oauth_value)
            if access_token.is_expired():
                request.authenticators = False
                return None
        except AccessToken.DoesNotExist:
            request.authenticators = False
            return None

        return access_token.user, oauth_value

    def get_oauth_value(self, request):
        auth = get_authorization_header(request).split()
        auth_header_prefix = "bearer"

        if not auth or smart_text(auth[0].lower()) != auth_header_prefix:
            return None

        if len(auth) == 1:
            msg = _('Invalid Authorization header. No credentials provided.')
            raise exceptions.PermissionDenied(msg)
        elif len(auth) > 2:
            msg = _('Invalid Authorization header. Credentials string '
                    'should not contain spaces.')
            raise exceptions.PermissionDenied(msg)

        return auth[1]