from rest_framework import serializers
from services.models import MobileOtp, UserDeviceToken


class MobileOtpSerializer(serializers.ModelSerializer):

    class Meta:
        model = MobileOtp
        fields = '__all__'


class UserDeviceTokenSerializer(serializers.ModelSerializer):
    """
    serializer to add device token
    """
    class Meta:
        model = UserDeviceToken
        fields = (
            'id',
            'user_id',
            'token',
            'device_type'
        )
        read_only_fields = ('id',)
