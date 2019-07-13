from datetime import datetime

from django.contrib.auth.models import User
from rest_framework import serializers

from accounts.models import UserProfile
from generic.database.users import UserModelQueries
from generic.misc.timezone import utc


class GetBasicUserDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class GetUserProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()
   
    @staticmethod
    def get_user_id(obj):
        user_obj = User.objects.get(id=obj.user_id)
        return GetBasicUserDataSerializer(instance=user_obj).data

    class Meta:
        model = UserProfile
        fields = ('id', 'user_id', 'nick_name', 'dob', 'blood_group', 'unique_id', 'level')


class UpdateUserProfileSerializer(serializers.ModelSerializer):
    # TODO: Validation for every data
    updated_timestamp = datetime.now(utc)

    class Meta:
        model = UserProfile
        fields = ('nick_name', 'dob', 'blood_group', 'updated_timestamp')
