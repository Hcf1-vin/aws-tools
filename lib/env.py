import os
import lib.profile as profile
from datetime import datetime
import requests
import logging


def set_env(aws_profile, aws_region):
    profile.check_profiles(aws_profile)
    if aws_profile != "default":
        os.environ["AWS-TOOLS-PROFILE"] = aws_profile
        logging.info(f"aws profile set to {os.environ['AWS-TOOLS-PROFILE']}")
        os.environ["AWS-TOOLS-REGION"] = aws_region
        logging.info(f"aws region set to {os.environ['AWS-TOOLS-REGION']}")


def clear_env():
    if os.environ.get("AWS-TOOLS-PROFILE") is not None:
        os.unsetenv("AWS-TOOLS-PROFILE")
        logging.info(f"aws profile unset")
    if os.environ.get("AWS-TOOLS-REGION") is not None:
        os.unsetenv("AWS-TOOLS-REGION")
        logging.info(f"aws region unset")


def convert_datetime(date_src):
    return date_src.strftime("%Y/%m/%d %H:%M")


def days_old(date_src):
    return (datetime.today() - date_src.replace(tzinfo=None)).days


def get_ip():
    return requests.get("http://ip.42.pl/raw").text + "/32"

