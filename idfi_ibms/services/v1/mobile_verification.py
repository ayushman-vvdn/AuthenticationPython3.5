from __future__ import unicode_literals
from rest_framework.views import APIView
from generic.response.http import StandardHttpResponse
from generic.misc.authentication import hasValidAuthHeaderMobile
from generic.misc.mailing import SentOTP
from generic.feature.otp import MobileOtpService
from generic.database.users import UserModelQueries
from generic.misc.timezone import utc
from datetime import datetime


class MobileOTP(APIView):

    permission_classes = (hasValidAuthHeaderMobile,)

    @staticmethod
    def required_data():
        return ["otp_type", "mobile"]

    def validate_request_data(self, request_data):
        req_data = self.required_data()

        for x in req_data:
            if x not in request_data or request_data[x] == '':
                return False
        return True

    def post(self, request):
        """
        To sent the otp on mobile for various purpose
        :param request:
        :return:
        """
        request_data = request.data.copy()
        user = request.user
        if not type(request_data) == dict:
            return StandardHttpResponse.bad_rsp([], 'Bad data')

        if not self.validate_request_data(request_data):
            return StandardHttpResponse.bad_rsp([], 'Missing data fields')

        mobile = request_data['mobile']

        user_profile = UserModelQueries.get_user_profile_by_mobile(mobile=mobile, mobile_verified=True)
        if user_profile:
            if user_profile.user.id == request.user.id:
                return StandardHttpResponse.bad_rsp([], 'Same Mobile number already registered with you.')
            else:
                return StandardHttpResponse.bad_rsp([], 'Mobile already registered.')

        user_profile_obj = UserModelQueries.get_user_profile_by_user_id(user.id)
        user_profile_obj.mobile = mobile
        user_profile_obj.is_active = False
        user_profile_obj.mobile_verified = False
        user_profile_obj.save()
        result, response = MobileOtpService.create_otp(mobile, o_type=request_data['otp_type'],
                                                       created_by=user.id)
        if result:
            resp = [{'otp_ref': response['otp_ref'], 'mobile': mobile}]
            return StandardHttpResponse.rsp_200(resp, 'An OTP sent to your Mobile. Please Verify it.')
        return StandardHttpResponse.bad_rsp([], response)


class MobileVerification(APIView):

    permission_classes = (hasValidAuthHeaderMobile,)

    @staticmethod
    def required_data():
        return ["otp", "otp_ref", "mobile"]

    def validate_request_data(self, request_data):
        req_data = self.required_data()

        for x in req_data:
            if x not in request_data or request_data[x] == '':
                return False
        return True

    def post(self, request):
        """
        Api to send an otp to mobile to verify it
        :param request:
        :return:
        """
        current_time = datetime.now(utc)
        request_data = request.data.copy()
        user = request.user
        if not type(request_data) == dict:
            return StandardHttpResponse.bad_rsp([], 'Bad data')

        if not self.validate_request_data(request_data):
            return StandardHttpResponse.bad_rsp([], 'Missing data fields')

        result, response = MobileOtpService.validate_otp(otp=request_data['otp'],
                                                         otp_ref=request_data['otp_ref'],
                                                         o_type='MobileVerification',
                                                         current_time=current_time)
        if not result:
            return StandardHttpResponse.bad_rsp([], response)
        if not response.mobile == request_data['mobile']:
            return StandardHttpResponse.bad_rsp([], 'Invalid Data')
        user_profile_obj = UserModelQueries.get_user_profile_by_user_id(user.id)
        if not user_profile_obj.mobile.__str__() == request_data['mobile']:
            return StandardHttpResponse.bad_rsp([], 'Invalid Data')
        user_profile_obj.mobile_verified = True
        user_profile_obj.is_active = True
        user_profile_obj.save()
        return StandardHttpResponse.rsp_200([], 'Mobile Verified.')


class ResendOTP(APIView):

    permission_classes = (hasValidAuthHeaderMobile,)

    @staticmethod
    def required_data():
        return ["otp_ref"]

    def validate_request_data(self, request_data):
        req_data = self.required_data()

        for x in req_data:
            if x not in request_data or request_data[x] == '':
                return False
        return True

    def post(self, request):
        """
        API to resend the OTP to mobile
        :param request:
        :return:
        """
        user = request.user
        request_data = request.data
        if not type(request_data) == dict:
            return StandardHttpResponse.bad_rsp([], 'Bad data')

        if not self.validate_request_data(request_data):
            return StandardHttpResponse.bad_rsp([], 'Missing data fields')

        result, response = MobileOtpService.resend_otp(request_data['otp_ref'])
        if not result:
            return StandardHttpResponse.bad_rsp([], response)
        user_profile_obj = UserModelQueries.get_user_profile_by_user_id(user.id)
        if not response.mobile.__str__() == user_profile_obj.mobile.__str__():
            return StandardHttpResponse.bad_rsp([], 'Invalid Data')
        response_data = [{'otp_ref': response.otp_ref}]
        return StandardHttpResponse.rsp_200(response_data, 'An OTP Sent to {} to reset the password'
                                            .format(response.mobile.__str__()))
