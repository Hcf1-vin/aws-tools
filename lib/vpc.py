import boto3
import configparser
import os
import lib.profile


def get_cidr_blocks():
    try:
        c_blocks = list()

        for aws_profile in lib.profile.get_aws_profiles():

            lib.env.set_env(aws_profile["name"], aws_profile["region"])
            ec2_client = lib.profile.create_sesssion(client_name="ec2")

            r = ec2_client.describe_vpcs()
            for vpc in r["Vpcs"]:
                for network in vpc["CidrBlockAssociationSet"]:
                    c_blocks.append(network["CidrBlock"])
            lib.env.clear_env()
        return c_blocks
    except:
        raise Exception("Error getting list of cidr blocks from aws")


def suggest_cidr():
    try:
        cidr_blocks = get_cidr_blocks()

        cidr_notation = 16
        upper_limit = 255
        starting_range = "10.0.0.0"
        starting_range_split = starting_range.split(".")

        r_count = 0
        range_used = True

        while range_used == True or r_count == 255:

            new_range = f"{starting_range_split[0]}.{r_count}.{starting_range_split[2]}.{starting_range_split[3]}/{cidr_notation}"

            if new_range in cidr_blocks:
                r_count += 1
            elif r_count > upper_limit:
                range_used = False
                raise Exception(
                    "I hoped this wouldn't ever happen, but we've reached the limits of this design"
                )
            else:
                range_used = False
                return new_range
    except:
        raise Exception("Error generating a new range")
