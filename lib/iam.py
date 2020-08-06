import lib.profile
import lib.env
import logging


def get_users():

    user_list = list()
    profile_list = lib.profile.get_aws_profiles()
    for p in profile_list:
        logging.info(p["name"])
        lib.env.set_env(p["name"], p["region"])
        iam_client = lib.profile.create_sesssion("iam")

        paginator = iam_client.get_paginator("list_users")

        response_iterator = paginator.paginate()

        for a in response_iterator:
            for b in a["Users"]:
                user_list.append(get_user_extended(b))

    return user_list


def get_user(iam_username):
    try:
        iam_client = lib.profile.create_sesssion("iam")

        response = iam_client.get_user(UserName=iam_username)

        return get_user_extended(response["User"])
    except:
        raise Exception(f"Error getting user - {iam_username}")


def get_user_extended(iam_user):
    user_dict = {}
    logging.info(iam_user["UserName"])
    user_dict["UserName"] = iam_user["UserName"]
    user_dict["CreateDate"] = lib.env.convert_datetime(iam_user["CreateDate"])
    if "PasswordLastUsed" in iam_user:
        user_dict["PasswordLastUsed"] = lib.env.convert_datetime(
            iam_user["PasswordLastUsed"]
        )
        user_dict["PasswordAge"] = lib.env.days_old(iam_user["PasswordLastUsed"])
    else:
        user_dict["PasswordLastUsed"] = "n/a"
        user_dict["PasswordAge"] = "n/a"

    user_dict["MfaEnabled"] = list_mfa_devices(iam_user["UserName"])

    access_keys = get_access_keys(iam_user["UserName"])

    for b in access_keys:
        index = str(access_keys.index(b))

        user_dict["AccessKeyId" + index] = b["AccessKeyId"]
        user_dict["Status" + index] = b["Status"]
        user_dict["CreateDate" + index] = lib.env.convert_datetime(b["CreateDate"])
        user_dict["DaysOld" + index] = lib.env.days_old(b["CreateDate"])

    for b in [0, 1]:
        index = str([0, 1].index(b))
        if ("AccessKeyId" + index) not in user_dict:
            user_dict["AccessKeyId" + index] = "n/a"
            user_dict["Status" + index] = "n/a"
            user_dict["CreateDate" + index] = "n/a"
            user_dict["DaysOld" + index] = "n/a"

    return user_dict


def get_password_profile(username):
    try:
        iam_client = lib.profile.create_sesssion("iam")
        response = iam_client.get_login_profile(UserName=username)
        return days_old(response["LoginProfile"]["CreateDate"])
    except:
        return "disabled"


def list_mfa_devices(username):
    iam_client = lib.profile.create_sesssion("iam")
    response = iam_client.list_mfa_devices(UserName=username)
    if response["MFADevices"] != []:
        mfa_enabled = "True"
    else:
        mfa_enabled = "False"

    return mfa_enabled


def get_access_keys(username):
    iam_client = lib.profile.create_sesssion("iam")
    response = iam_client.list_access_keys(UserName=username,)

    return response["AccessKeyMetadata"]
