from services.serializers import MobileOtpSerializer
from generic.database.otp import MobileOtpModelQueries
from generic.misc.timezone import utc
import string
import random
from datetime import datetime, timedelta


class MobileOtpService(object):

    @staticmethod
    def get_otp_type(name, is_resend=False):
        """
        Get the type code for
        :param name:
        :param is_resend:
        :return:
            Otp type code
        """
        response = {"SignUp": "SG",
                    "LoginOtp": "LO",
                    "MobileVerification": "MV",
                    "ForgetPassword": "FP"}
        if is_resend:
            for key, values in response.iteritems():
                if name == values:
                    return key
        if name not in response:
            return False
        return response[name]

    @staticmethod
    def generate_otp():
        otp = ''.join(random.choice(string.digits) for tmp in range(6))
        if MobileOtpModelQueries.get_mobile_otp_by_otp(otp):
            return MobileOtpService.generate_otp()
        return otp

    @staticmethod
    def generate_otp_ref():
        otp = ''.join(random.choice(string.digits) for tmp in range(8))
        if MobileOtpModelQueries.get_mobile_otp_by_otp_ref(otp):
            return MobileOtpService.generate_otp_ref()
        return otp

    @staticmethod
    def create_otp(mobile, o_type, email=None, created_by=None):
        """
        creating an otp
        :param mobile :
        :param o_type :
        :param email:
        :param created_by:
        :return:
            True, otp_ref (Otp Reference number)
        """
        data = dict()
        data['mobile'] = mobile
        data['email'] = email
        otp_type = MobileOtpService.get_otp_type(o_type)
        if not otp_type:
            return False, 'OTP Type not found'
        data['validation_type'] = otp_type
        data['otp'] = MobileOtpService.generate_otp()
        data['otp_ref'] = MobileOtpService.generate_otp_ref()
        if created_by:
            data['created_by'] = created_by
        data['expired'] = datetime.now(utc)

        serializer = MobileOtpSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            return False, serializer.errors
        return True, data

    @staticmethod
    def resend_otp(otp_ref):
        """
        To resend the otp with otp ref
        :return:
        """
        otp_obj = MobileOtpModelQueries.get_mobile_otp_by_otp_ref(otp_ref=otp_ref)
        if not otp_obj:
            return False, 'We are unable to process your request now, Please try again after sometime.'
        if otp_obj.resend > 2:
            return False, 'You have exceeded the limit of resend OTP. Please try again.'
        if not otp_obj.validation_type == 'MV':
            return False, 'Resend OTP is not enable for this.'
        new_otp = MobileOtpService.generate_otp()
        resend = otp_obj.resend + 1
        otp_obj.otp = new_otp
        otp_obj.expired = datetime.now(utc)
        otp_obj.resend = resend
        otp_obj.save()
        return True, MobileOtpModelQueries.get_mobile_otp_by_otp_ref(otp_ref=otp_ref)

    @staticmethod
    def validate_otp(otp, otp_ref, o_type, current_time, return_obj=None):
        """
        To validate the otp entered by customer
        :param otp:
        :param otp_ref:
        :param o_type:
        :param current_time: (datetime type)
        :param return_obj
        :return:
        """
        otp_type = MobileOtpService.get_otp_type(o_type)
        if not otp_type:
            return False, 'Invalid OTP'
        otp_info = MobileOtpModelQueries.get_mobile_otp(otp_ref=otp_ref, validation_type=otp_type)
        if not otp_info:
            return False, 'Invalid OTP'
        # TODO ---------------------This code is Temp because of SMS Facility W'll remove it-----------------------
        if otp == '888888':
            return True, otp_info
        # ---------------------------------------------------------------------------------------------------------

        # Check whether otp Expired
        if (otp_info.expired - current_time).total_seconds() < -180.0:
            otp_info.delete()
            return False, 'OTP Expired'

        # Check whether OTP matched
        if otp == otp_info.otp:
            if return_obj:
                return True, otp_info
            else:
                otp_info.delete()
                return True, 'OTP Verified.'

        return False, 'Invalid OTP'
