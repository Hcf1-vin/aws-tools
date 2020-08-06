import boto3
import configparser
import os


def check_profiles(aws_profile):
    try:
        exists = False
        if aws_profile == "default":
            exists = True
        for profile in get_aws_profiles():
            if aws_profile == profile["name"]:
                exists = True

        if exists == False:
            raise Exception(f"no such profile - {aws_profile}")
    except:
        raise Exception(f"Error validating aws profile")


def get_aws_profiles():
    try:
        path = os.path.join(os.path.expanduser("~"), ".aws/config")
        parser = configparser.RawConfigParser()
        parser.read(path)

        profile_list = list()
        for profile in parser.sections():
            if "profile" in profile:
                profile_dict = dict()
                profile_dict["name"] = profile.replace("profile ", "")

                profile_items = parser.items(profile)
                for key, value in profile_items:
                    profile_dict[key] = value
                profile_list.append(profile_dict)

        return profile_list
    except:
        raise Exception(f"Error getting list of profiles from {path}")


def create_sesssion(client_name: str = "sts",):

    if os.environ.get("AWS-TOOLS-PROFILE") is not None:
        aws_profile = os.environ["AWS-TOOLS-PROFILE"]
    else:
        aws_profile = "default"

    if os.environ.get("AWS-TOOLS-REGION") is not None:
        aws_region = os.environ["AWS-TOOLS-REGION"]
    else:
        aws_region = "eu-west-1"

    session = boto3.session.Session(profile_name=aws_profile, region_name=aws_region)
    return session.client(client_name)
