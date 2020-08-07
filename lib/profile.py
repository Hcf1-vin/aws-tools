import boto3
import configparser
import os
import lib.file
from jinja2 import Template
import logging
import re


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


def create_default():
    aws_dir = os.path.join(os.path.expanduser("~"), ".aws")
    aws_credential = os.path.join(aws_dir, "credentials")
    aws_config = os.path.join(aws_dir, "config")
    lib.file.create_dir(aws_dir)
    logging.warn(f"{aws_credential} will be overwritten")
    logging.warn(f"{aws_config} will be overwritten")

    def _create_config(aws_region, aws_output):
        t = Template(
            """[default]
region = {{aws_region}}
output = {{aws_output}}"""
        )

        return t.render(aws_region=aws_region, aws_output=aws_output)

    def _create_credentials(aws_access, aws_secret):
        t = Template(
            """[default]
aws_access_key_id = {{aws_access}} 
aws_secret_access_key = {{aws_secret}}"""
        )

        return t.render(aws_access=aws_access, aws_secret=aws_secret)

    def _validate_keys(input_string, check_type):
        lib.ec2.get_regions()

        logging.info(f"validate aws {check_type} format")
        if check_type == "key":
            re_check = "(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])"
        elif check_type == "secret":
            re_check = "(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])"
        else:
            raise Exception(f"unknown check_type: {check_type}")

        regex = re.compile(re_check, re.I)

        match = regex.match(str(input_string))
        if bool(match) == False:
            raise Exception(f"invalid {check_type}")

    aws_access = input("Please enter your aws access key:\n")
    aws_secret = input("Please enter your aws secret key:\n")
    aws_region = input("Please enter your aws region:\n")
    aws_output = "json"

    _validate_keys(aws_access, check_type="key")
    _validate_keys(aws_secret, check_type="secret")
    validate_region(aws_region)

    lib.file.write_file(_create_config(aws_region, aws_output), aws_config)
    lib.file.write_file(_create_credentials(aws_access, aws_secret), aws_credential)


def validate_region(aws_region):
    aws_regions = lib.ec2.get_regions()
    if aws_region not in aws_regions:
        raise Exception(
            f"{aws_region} in not a valid region. must be one of {aws_regions}"
        )


def create_config():
    pass
