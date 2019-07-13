from __future__ import unicode_literals
from rest_framework.views import APIView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth import authenticate
from django.utils.decorators import method_decorator
from generic.response.http import StandardHttpResponse
from generic.database.users import UserModelQueries
from generic.misc.authentication import hasValidAuthHeader
from generic.misc.validation import ValidationClass
from oauth2_provider.decorators import protected_resource
from accounts.accounts_serializers.users import UpdateUserProfileSerializer, GetUserProfileSerializer


class NickNameValidation(APIView):
    """
    To check whether the nick name available or not
    """

    def get(self, request):
        """

        :param request:
        :return:
        """
        nick_name = request.GET.get("nick_name", None)
        if not nick_name:
            return StandardHttpResponse.bad_rsp([], 'Missing Data')
        response = UserModelQueries.get_user_profile_by_nick_name(nick_name)
        if response:
            return StandardHttpResponse.bad_rsp([], 'NickName already taken.')
        return StandardHttpResponse.rsp_200([], 'NickName available.')


class UserProfileList(APIView):
    permission_classes = (hasValidAuthHeader,)

    def get(self, request):
        """
        Get the list of users for Admin purpose
        :param request:
        :return:
        """
        user = request.user
        nick_name = request.GET.get('nick_name', None)
        mobile = request.GET.get('mobile', None)
        email = request.GET.get('email', None)
        unique_id = request.GET.get('unique_id', None)
        if user.is_superuser:
            user_data = UserModelQueries.get_all_user_profile()
        elif mobile:
            user_data = UserModelQueries.get_user_profile_by_mobile()
        elif email:
            user_data = UserModelQueries.get_user_profile_by_email()
        elif unique_id:
            user_data = UserModelQueries.get_user_profile_by_unique_id()
        elif nick_name:
            user_data = UserModelQueries.get_user_profile_by_nick_name()
        else:
            return StandardHttpResponse.bad_rsp([], 'Invalid Search.')
        paginator = Paginator(user_data, 30)
        page = request.GET.get('page', 1)
        try:
            user_data = paginator.page(page)
        except PageNotAnInteger:
            return StandardHttpResponse.bad_rsp([], 'Not a valid Page Number.')
        except EmptyPage:
            return StandardHttpResponse.rsp_200([], 'No User Found')
        serializer = GetUserProfileSerializer(instance=user_data, many=True)
        return StandardHttpResponse.rsp_200(serializer.data, 'User fetched Successfully.')


class UserProfileDetails(APIView):

    permission_classes = (hasValidAuthHeader,)

    def get(self, request):
        """
        To get the profile details
        :param request:
        :return:
        """
        user = request.user
        user_obj = UserModelQueries.get_user_profile_by_user_id(user.id)
        serializer = GetUserProfileSerializer(instance=user_obj)
        return StandardHttpResponse.rsp_200(serializer.data, 'Profile fetched Successfully.')

    def post(self, request):
        """
        To edit the user profile
        :param request:
        :return:
        """
        request_data = request.data.copy()

        if not type(request_data) == dict:
            return StandardHttpResponse.bad_rsp([], 'Bad data')

        user = request.user
        user_profile_obj = UserModelQueries.get_user_profile_by_user_id(user.id)
        if 'nick_name' in request_data:
            response = UserModelQueries.get_user_profile_by_nick_name(request_data['nick_name'])
            if response and not response.user_id == user.id:
                return StandardHttpResponse.bad_rsp([], 'Nick Name already taken.')
        if 'dob' in request_data:
            result, dob1 = ValidationClass.validate_dob(request_data['dob'])
            if not result:
                return StandardHttpResponse.bad_rsp([], dob1)
            request_data['dob'] = dob1
        serializer = UpdateUserProfileSerializer(instance=user_profile_obj, data=request_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if 'first_name' in request_data or 'last_name' in request_data:
                user_obj = UserModelQueries.get_user_by_id(user.id)
                if 'first_name' in request_data and request_data['first_name']:
                    user_obj.first_name = request_data['first_name']
                if 'last_name' in request_data and request_data['last_name']:
                    user_obj.last_name = request_data['last_name']
                user_obj.save()
            # -------This is extra query load on database because of Android demand---
            user_profile_obj = UserModelQueries.get_user_profile_by_user_id(user.id)
            response_data = GetUserProfileSerializer(instance=user_profile_obj).data
            # ------------------------------------------------------------------------
            return StandardHttpResponse.rsp_200(response_data, 'User Profile Updated Successfully')
        return StandardHttpResponse.bad_rsp([], serializer.errors)


class ChangePassword(APIView):

    permission_classes = (hasValidAuthHeader, )

    @staticmethod
    def required_data():
        return ["old_password", "new_password", "confirm_new_password"]

    def validate_request_data(self, request_data):
        req_data = self.required_data()

        for x in req_data:
            if x not in request_data or request_data[x] == '':
                return False
        return True

    def post(self, request):
        original_request_data = request.data.copy()
        user = request.user

        if not type(original_request_data) == dict:
            return StandardHttpResponse.bad_rsp([], 'Bad data')

        if not self.validate_request_data(original_request_data):
            return StandardHttpResponse.bad_rsp([], 'Missing data fields')

        if not original_request_data['new_password'] == original_request_data['confirm_new_password']:
            return StandardHttpResponse.bad_rsp([], 'Password and Confirm Password not matched.')
        old_password = original_request_data['old_password']

        user_obj = UserModelQueries.get_user_by_id(user.id)
        authenticated_user = authenticate(username=user_obj.username, password=old_password)
        if not authenticated_user:
            return StandardHttpResponse.login_bad_rsp([], 'Old Password not matched')

        user_obj.set_password(original_request_data['new_password'])
        user_obj.save()
        return StandardHttpResponse.rsp_200([], 'Password Changed Successfully.')

