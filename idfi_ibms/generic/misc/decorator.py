from functools import wraps
from generic.misc.authentication import get_authorization_header
from rest_framework import exceptions
from oauth2_provider.models import AccessToken
from generic.response.http import StandardHttpResponse
from django.utils.translation import ugettext_lazy as _


def check_permission(scopes=None):
    """
    Check the scopes
    :param scopes:
    :return:
    """
    _scopes = scopes or []

    def decorator(view_func):
        @wraps(view_func)
        def _validate(request, *args, **kwargs):
            auth = get_authorization_header(request).split()
            if not auth or auth[0].lower() != 'Token'.lower().encode():
                msg = _('Invalid token. Token string should not contain spaces.')
                raise exceptions.AuthenticationFailed(msg)
            if len(auth) == 1:
                msg = _('Invalid token. No credentials provided.')
                raise exceptions.AuthenticationFailed(msg)
            elif len(auth) > 2:
                msg = _('Invalid token. Token string should not contain spaces.')
                raise exceptions.AuthenticationFailed(msg)
            try:
                token = auth[1].decode()
            except UnicodeError:
                msg = _('Invalid token header. Token string should not contain invalid characters.')
                raise exceptions.AuthenticationFailed(msg)

            try:
                access_token = AccessToken.objects.get(token=token)
                if access_token.is_expired():
                    request.authenticators = False
                    raise exceptions.AuthenticationFailed('Invalid token.')
            except AccessToken.DoesNotExist:
                request.authenticators = False
                raise exceptions.AuthenticationFailed('Invalid token.')

            token = access_token.user
            if not token:
                raise exceptions.AuthenticationFailed('Invalid token.')
            perm = False if len(_scopes) > 0 else True
            if token.is_superuser:
                perm = True
            elif token.permission_string:
                permissions = _(token.permission_string).split(',')
                for val in _scopes:
                    # The list will be OR
                    if type(val) == tuple:
                        for z in val:
                            if z in permissions:
                                perm = True

                    else:
                        if val in permissions:
                            perm = True
                        else:
                            perm = False
            if perm:
                return view_func(request, *args, **kwargs)
            return StandardHttpResponse.rsp_401([], 'You are not authorized.')

        return _validate

    return decorator
