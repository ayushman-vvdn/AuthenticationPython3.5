from __future__ import unicode_literals
from django.contrib.auth.models import User
from accounts.models import UserProfile
from time import time
from generic.misc.validation import ValidationClass
from generic.database.users import UserModelQueries


class UserUtils(object):

    @staticmethod
    def user_validation(data):
        if 'first_name' in data:
            result, response = ValidationClass.validate_alphabet('first_name', data['first_name'])
            if not result:
                return False, response
        if 'last_name' in data:
            result, response = ValidationClass.validate_alphabet('last_name', data['last_name'])
            if not result:
                return False, response
        if 'email' in data:
            result, response = ValidationClass.validate_email(data['email'])
            if not result:
                return False, response
        return True, ''

    @staticmethod
    def user_profile_validation(data):
        if 'nick_name' in data:
            result, response = ValidationClass.validate_alphanumeric_with_special('Nick Name',
                                                                                  data['nick_name'])
            if not result:
                return False, response
        return True, ''

    @staticmethod
    def create_unique_id(first_name):
        # to maintain the first_name
        first_name = first_name.upper()
        if len(first_name) < 3:
            first_name += 'XXX'

        unique_no = int(time()*1000).__str__()
        unique_id = first_name[:3] + unique_no
        return unique_id

    @staticmethod
    def create_user(first_name, last_name, username, password):
        """
        To create the user
        :param first_name:
        :param last_name:
        :param email:
        :param password:
        :return:
        """
        data = dict()
        data['first_name'] = first_name
        data['last_name'] = last_name
        data['username'] = username
        # data['email'] = email.lower()
        data['is_active'] = True
        result, response = UserUtils.user_validation(data)
        if not result:
            return False, response
        try:
            user_obj = User.objects.create(**data)
        except Exception as e:
            return False, e.__str__()
        user_obj.set_password(password)
        user_obj.save()
        return True, user_obj

    @staticmethod
    def create_user_profile(user, mobile=None, blood_group=None, dob=None, nick_name=None):
        """
        To create the user_profile
        :param user:
        :param mobile:
        :param blood_group:
        :param dob:
        :param nick_name:
        :return:
        """
        data = dict()
        data['user_id'] = user.id
        data['blood_group'] = blood_group
        if dob:
            result, dob1 = ValidationClass.validate_dob(dob)
            if not result:
                return False, dob1
            data['dob'] = dob1
        data['nick_name'] = nick_name
        data['unique_id'] = UserUtils.create_unique_id(user.first_name)
        try:
            user_obj = UserProfile.objects.create(**data)
        except Exception as e:
            return False, e.__str__()
        return True, user_obj
