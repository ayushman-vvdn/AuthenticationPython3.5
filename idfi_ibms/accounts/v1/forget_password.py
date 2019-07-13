from __future__ import unicode_literals
from rest_framework.views import APIView
from idfi_ibms.settings import REDIRECT_URL
from generic.misc.oauth_provider import TokenView
from generic.response.http import StandardHttpResponse
from generic.database.users import UserModelQueries
from generic.misc.timezone import utc
from datetime import datetime
import urllib
import json


class ForgetPassword(APIView):

    def post(self, request):
        """
        Api to send the link on mail for forget password
        :param request:
        :return:
        """
        request_data = request.data
        if 'mobile' not in request_data or not request_data['mobile']:
            return StandardHttpResponse.bad_rsp([], 'Invalid Data.')
        email = None
        mobile = None
        if '@' in request_data['mobile']:
            email = request_data['mobile']
        else:
            mobile = request_data['mobile']
        if mobile:
            user_profile_obj = UserModelQueries.get_user_profile_by_mobile(mobile)
            if not user_profile_obj:
                return StandardHttpResponse.bad_rsp([], 'Mobile is yet not registered or not verified.')
        else:
            user_profile_obj = UserModelQueries.get_user_profile_by_email(email)
            if not user_profile_obj:
                return StandardHttpResponse.bad_rsp([], 'Looks like You haven\'t registered yet. Please Registered.')

        result, response = MobileOtpService.create_otp(user_profile_obj.mobile,
                                                       'ForgetPassword')
        if not result:
            return StandardHttpResponse.bad_rsp([], response)
        # TODO: Code to send the otp to mobile
        SentOTP.send_otp_to_email(email, response['otp'], 'Forget Password')
        response_data = {'otp_ref': response['otp_ref']}
        return StandardHttpResponse.rsp_200(response_data, 'An OTP Sent to {} to reset the password'
                                            .format(user_profile_obj.mobile.__str__()))


class PasswordResetUtils(object):

    @staticmethod
    def required_data():
        return ["otp", "otp_ref", "password", "confirm_password"]

    @staticmethod
    def validate_request_data(request_data):
        req_data = PasswordResetUtils().required_data()

        for x in req_data:
            if x not in request_data or request_data[x] == '':
                return False
        return True


def PasswordResetViaOTP(request):
    """
    TO reset the password for a user via otp
    :param request:
    :return:
    """
    current_time = datetime.now(utc)
    request_data = json.loads(request.body)

    if not type(request_data) == dict:
        return StandardHttpResponse.login_bad_rsp([], 'Bad data')

    if not PasswordResetUtils().validate_request_data(request_data):
        return StandardHttpResponse.login_bad_rsp([], 'Missing data fields')

    if not request_data['password'] == request_data['confirm_password']:
        return StandardHttpResponse.login_bad_rsp([], 'Password Not Matched')

    result, response = MobileOtpService.validate_otp(otp=request_data['otp'],
                                                     otp_ref=request_data['otp_ref'],
                                                     o_type='ForgetPassword',
                                                     current_time=current_time,
                                                     return_obj=True)
    if not result:
        return StandardHttpResponse.login_bad_rsp([], response)
    if not response.mobile:
        return StandardHttpResponse.login_bad_rsp([], 'Invalid request. Please contact Admin.')
    user_profile_obj = UserModelQueries.get_user_profile_by_mobile(response.mobile)
    if not user_profile_obj:
        return StandardHttpResponse.login_bad_rsp([], 'Mobile not registered')
    user_obj = UserModelQueries.get_user_by_id(user_profile_obj.user_id)
    response.delete()
    user_obj.set_password(request_data['password'])
    user_obj.save()
    json_body = dict()
    json_body['username'] = user_obj.username
    json_body['password'] = request_data['password']
    json_body['grant_type'] = 'password'
    request._body = urllib.urlencode(json_body)
    json_body['redirect_uri'] = REDIRECT_URL
    request._post = json_body
    view = TokenView.as_view()
    request.META[
        "HTTP_AUTHORIZATION"] = "Basic YlVhOFBCTTFCQTFGb3JPUlp5RVB0RmFBSUJZOGNhUWF5N2hTbTE4dDpla25ENkVzenlJZEZMeUM1RmhqSFlnUnVuMlk2alpqMTN0Mll1ZzZhVWNJc0ZYYk9VMnNyWDRjRmJLQkpwMnpVVVRZNnV6U0U5V3AyN3JJTmNPZ09FWmVDVlB4NXVEWXV0ZHBFMHhVcEROTTBGUlluRERMQzlTTnNNN3RRZUhEbA=="
    request.META["CONTENT_TYPE"] = "application/x-www-form-urlencoded"
    return StandardHttpResponse.login_rsp(json.loads(view(request).content), 'User Logged-In Successfully.')
