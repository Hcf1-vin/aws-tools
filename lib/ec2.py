import boto3
import lib.profile as profile
import lib.env
import lib.file
import os
import logging


def get_ec2(lite=False):
    ec2_list = list()
    ec2_client = profile.create_sesssion(client_name="ec2")
    paginator = ec2_client.get_paginator("describe_instances")

    response_iterator = paginator.paginate()

    for a in response_iterator:
        for b in a["Reservations"]:
            for c in b["Instances"]:
                if lite == False:
                    ec2_list.append(c)
                else:
                    ec2_list.append(c["InstanceId"])

    return ec2_list


def get_tags(instance_id):
    tag_list = list()
    ec2_client = profile.create_sesssion(client_name="ec2")
    response = ec2_client.describe_tags(
        Filters=[{"Name": "resource-id", "Values": [instance_id]},]
    )
    for a in response["Tags"]:
        tag_dict = dict()
        tag_dict[a["Key"]] = a["Value"]
        tag_list.append(tag_dict)

    return tag_list


def get_ami_user(ami_id):
    ec2_client = profile.create_sesssion(client_name="ec2")
    response = ec2_client.describe_images(ImageIds=[ami_id])

    for a in response["Images"]:
        if a["OwnerId"] in ["602401143452", "286198878708"]:
            return "ec2-user"
        else:
            return "ubuntu"


def generate_ssh_config():
    instance_list = list()
    profile_list = profile.get_aws_profiles()
    logging.info(profile_list)
    for p in profile_list:
        lib.env.set_env(p["name"], p["region"])
        for i in get_ec2():
            if not i.get("Platform"):

                instance = {}
                instance["ip"] = i["PrivateIpAddress"]

                instance["key"] = (
                    os.path.expanduser("~") + "/.ssh/" + i["KeyName"] + ".pem"
                )

                instance["user"] = get_ami_user(i["ImageId"])

                if i.get("Tags"):
                    for t in i["Tags"]:
                        if t["Key"] == "Name":
                            instance["name"] = t["Value"]

                            instance_list.append(instance)
                logging.info(instance)
        lib.env.clear_env()

    conf_content = lib.file.render_template(instance_list, "ssh_config.j2")
    lib.file.write_file(conf_content, os.path.expanduser("~/.ssh/config"))


def get_regions():
    ec2_client = profile.create_sesssion(client_name="ec2")
    response = ec2_client.describe_regions()
    role_list = []
    for r in response["Regions"]:
        role_list.append(r["RegionName"])

    return role_list


def validate_region(aws_region):
    aws_regions = get_regions()
    if aws_region not in aws_regions:
        raise Exception(
            f"{aws_region} in not a valid region. must be one of {aws_regions}"
        )
