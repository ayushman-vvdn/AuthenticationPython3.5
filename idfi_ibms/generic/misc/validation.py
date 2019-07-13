from __future__ import unicode_literals
import re
from datetime import datetime


class ValidationClass(object):

    @staticmethod
    def validate_alphabet(key, value):
        if not re.match('^[a-zA-Z. ]*$', str(value)):
            return False, '{} should contains only alphabets.'.format(key)
        return True, ''

    @staticmethod
    def validate_alphanumeric(key, value):
        if not re.match('^[a-zA-Z0-9.]*$', str(value)):
            return False, '{} should contains only alphabets and numbers'.format(key)
        return True, ''

    @staticmethod
    def validate_alphanumeric_with_special(key, value):
        if not re.match('^[a-zA-Z0-9-#$@!.]*$', str(value)):
            return False, '{} should contains only alphabets and numbers and special ' \
                          'character (-#$@!.)'.format(key)
        return True, ''


    @staticmethod
    def validate_email(email):
        if not re.match('^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,})$',
                        email):
            return False, 'E-Mail is invalid.'
        return True, ''

    @staticmethod
    def validate_dob(dob):
        try:
            dob = datetime.strptime(dob, '%Y-%m-%d')
            return True, datetime.date(dob)
        except (TypeError, ValueError):
            return False, "DOB is in wrong format"
