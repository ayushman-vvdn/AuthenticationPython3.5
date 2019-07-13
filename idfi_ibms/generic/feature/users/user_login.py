from __future__ import unicode_literals
from oauth2_provider.models import AccessToken
from generic.database.users import UserModelQueries
from generic.feature.users.user_utils import UserUtils


def real_login_helper(user):
    """Authenticate user."""
    try:
        response_data = {}
        if not user:
            return False, {}

        user_obj = UserModelQueries.get_user_profile_by_user_id(user.id)
        response_data["auth"] = "success"
        response_data["user_id"] = str(user.id)
        response_data["login"] = True
        response_data["first_name"] = user.first_name
        response_data["last_name"] = user.last_name
        response_data["nick_name"] = user_obj.nick_name
        response_data["level"] = user_obj.level
        response_data["points"] = user_obj.points
        response_data["unique_id"] = user_obj.unique_id

        if not user_obj:
            UserUtils.create_user_profile(user)
            user_obj = UserModelQueries.get_user_profile_by_user_id(user.id)

        if user_obj.profile_pic:
            response_data["profile_pic"] = "https://s3.ap-south-1.amazonaws.com/{}/{}".format(
                user_obj.profile_pic.bucket, user_obj.profile_pic.key)

        response_data['email'] = user.email
        response_data['mobile'] = user_obj.mobile
        response_data['mobile_verified'] = user_obj.mobile_verified
        response_data['email_verified'] = user_obj.email_verified
        response_data['is_active'] = user_obj.is_active
        response_data['admin'] = user.is_superuser
        response_data['unique_id'] = user_obj.unique_id
        response_data['bicycle_profile'] = user_obj.bicycle_profile
        response_data['bike_profile'] = user_obj.bike_profile
        response_data['car_profile'] = user_obj.car_profile
        response_data['interest'] = user_obj.interest
        return True, response_data
    except Exception as err:
        return False, {'err': str(err)}


def real_login_helper_token(token):
    try:
        user = AccessToken.objects.get(token=token).user
    except AccessToken.DoesNotExist:
        return False, {}

    return real_login_helper(user=user)
