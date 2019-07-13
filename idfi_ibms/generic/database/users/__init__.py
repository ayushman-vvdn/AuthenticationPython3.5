from __future__ import unicode_literals
from accounts.models import UserProfile
from django.contrib.auth.models import User


class UserModelQueries(object):

    @staticmethod
    def get_user_profile_by_user_id(user_id):
        try:
            return UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return False

    @staticmethod
    def get_user_by_username(username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return False

    @staticmethod
    def get_user_by_id(_id):
        try:
            return User.objects.get(id=_id)
        except User.DoesNotExist:
            return False

    @staticmethod
    def get_user_profile_by_nick_name(nick_name):
        try:
            return UserProfile.objects.get(nick_name=nick_name)
        except UserProfile.DoesNotExist:
            return False

    @staticmethod
    def get_user_profile_by_mobile(mobile, mobile_verified=True):
        try:
            return UserProfile.objects.get(mobile=mobile, mobile_verified=mobile_verified)
        except UserProfile.DoesNotExist:
            return False

    @staticmethod
    def get_all_user_profile():
        return UserProfile.objects.all()

    @staticmethod
    def get_user_by_email(email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return False

    @staticmethod
    def get_user_profile_by_unique_id(unique_id):
        try:
            return UserProfile.objects.get(unique_id=unique_id)
        except UserProfile.DoesNotExist:
            return False

    @staticmethod
    def get_user_profile_by_email(email):
        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            return False
        return UserModelQueries.get_user_profile_by_user_id(user_obj.id)

    @staticmethod
    def validate_user_by_id(_id):
        try:
            return User.objects.get(id=_id)
        except User.DoesNotExist:
            return False
