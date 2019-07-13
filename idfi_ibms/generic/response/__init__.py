# -*- coding:utf-8 -*-
from __future__ import unicode_literals

__all__ = ['MessageResponse']


class MessageResponse(object):

    @staticmethod
    def error_response(err, message):
        return {'error': err, 'message': message, 'success': False}

    @staticmethod
    def success_response(success, message):
        return {'success': success, 'message': message, 'error': False}
