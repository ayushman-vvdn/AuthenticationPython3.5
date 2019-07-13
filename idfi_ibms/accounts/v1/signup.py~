from __future__ import unicode_literals
from rest_framework.views import APIView
from generic.response.http import StandardHttpResponse
from generic.database.users import UserModelQueries
from generic.feature.users.user_utils import UserUtils
from idfi_ibms.settings import API_DOMAIN
import requests
import json


class Signup(APIView):

    @staticmethod
    def required_data():
        return ["name", "password"]

    def validate_request_data(self, request_data):
        req_data = self.required_data()

        for x in req_data:
            if x not in request_data or request_data[x] == '':
                return False
        return True

    def post(self, request):
        """
        To create a user
        :param request:
        :return:
        """
        request_data = request.data.copy()

        if not type(request_data) == dict:
            return StandardHttpResponse.bad_rsp([], 'Bad data')

        if not self.validate_request_data(request_data):
            return StandardHttpResponse.bad_rsp([], 'Missing data fields')

        name_arr = request_data['name'].split(' ')
        if len(name_arr) > 1:
            last_name = name_arr[-1:][0]
            name_arr.remove(last_name)
            first_name = ''
            for i in name_arr:
                if i:
                    first_name = first_name + ' ' + i
            first_name = first_name.lstrip()
        else:
            first_name = request_data['name']
            last_name = ''
        result, user_response = UserUtils.create_user(first_name=first_name,
                                                      last_name=last_name,
							username=first_name,
                                                      password=request_data['password'])
        if not result:
            return StandardHttpResponse.bad_rsp([], user_response)
        blood_group = dob = None
        if 'blood_group' in request_data and request_data['blood_group']:
            blood_group = request_data['blood_group']
        if 'dob' in request_data and request_data['dob']:
            dob = request_data['dob']
        result, user_profile_response = UserUtils.create_user_profile(user=user_response,
                                                                      blood_group=blood_group,
                                                                      dob=dob)
        if not result:
            user_response.delete()
            return StandardHttpResponse.bad_rsp([], user_profile_response)

        data = {"username": first_name,
                "password": request_data['password'],
                "grant_type": "password"}

        response = requests.post(API_DOMAIN + '/v1/login/', json=data)
        if response.status_code == 200:
            data = json.loads(response.text)
            return StandardHttpResponse.rsp_201(data['success'], 'User Created Successfully.')
        else:
            return StandardHttpResponse.rsp_200([], 'User Created Successfully.')

