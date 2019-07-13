from services.models import MobileOtp


class MobileOtpModelQueries(object):

    @staticmethod
    def get_mobile_otp(otp_ref, validation_type):
        """
        return MobileOtp object based on otp_ref and type
        :param otp_ref:
        :param validation_type:
        :return:
        """
        try:
            return MobileOtp.objects.get(otp_ref=otp_ref, validation_type=validation_type)
        except MobileOtp.DoesNotExist:
            return False

    @staticmethod
    def get_mobile_otp_by_otp_ref(otp_ref):
        """
        return MobileOtp object based on otp_ref
        :param otp_ref:
        :return:
        """
        try:
            return MobileOtp.objects.get(otp_ref=otp_ref)
        except MobileOtp.DoesNotExist:
            return False

    @staticmethod
    def get_mobile_otp_by_otp(otp_ref):
        """
        return MobileOtp object based on otp_ref
        :param otp_ref:
        :return:
        """
        try:
            return MobileOtp.objects.get(otp=otp_ref)
        except MobileOtp.DoesNotExist:
            return False
