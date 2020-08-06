import lib.profile
import lib.vpc
import lib.ec2
import lib.iam
import lib.file
import lib.env
import lib.route53
import os
import click
import atexit
import logging


@click.group()
@click.option(
    "--profile",
    "-p",
    nargs=1,
    default="default",
    help="aws profile name. default value = default",
)
@click.option(
    "--region",
    "-r",
    nargs=1,
    default="eu-west-1",
    help="aws region. default value = eu-west-1",
)
@click.option(
    "--debug", nargs=1, default=False, type=bool, help="enable debug", is_flag=True,
)
def main(profile, region, debug):
    if debug == True:
        logging.basicConfig(level=logging.INFO)
    lib.env.set_env(profile, region)
    pass


@atexit.register
def main_results():
    lib.env.clear_env()


@main.command()
def ssh_config():
    lib.ec2.generate_ssh_config()


@main.group()
def cidr():
    pass


@cidr.command()
def list_cidr():
    r = lib.vpc.get_cidr_blocks()
    print(r)


@cidr.command()
def gen_cidr():
    r = lib.vpc.suggest_cidr()
    print(r)


@main.group()
def ec2():
    pass


@ec2.command()
@click.option(
    "--lite",
    help="only returns instance id. use --profile if not default profile",
    default=False,
    is_flag=True,
)
def list_ec2(lite):
    r = lib.ec2.get_ec2(lite)
    print(r)


@main.group()
def iam():
    pass


@iam.command()
@click.option(
    "--username",
    "-u",
    help="gets user information for specfieid user. use --profile if not default profile",
    default=None,
)
@click.option(
    "--all",
    "-a",
    nargs=1,
    help="lists users across all profiles",
    type=bool,
    default=False,
    is_flag=True,
)
@click.option(
    "--output",
    "-o",
    nargs=1,
    help="output to file. only availble for --all",
    type=bool,
    default=False,
    is_flag=True,
)
def get_user(username, all, output):
    if all == True:
        r = lib.iam.get_users()
        if output == True:
            lib.file.write_csv(r)
        else:
            print(r)
    elif username != None:
        r = lib.iam.get_user(username)
        print(r)


@main.group()
def profile():
    pass


@profile.command()
def list_profiles():
    r = lib.profile.get_aws_profiles()
    for a in r:
        print(a)


@main.group()
def r53():
    pass


@r53.command()
def get_zones(output):
    r = lib.route53.get_zones()
    print(r)


@r53.command()
@click.option(
    "--output",
    "-o",
    nargs=1,
    help="output to file",
    type=bool,
    default=False,
    is_flag=True,
)
@click.option(
    "--id", "-i", nargs=1, help="zone id", default=None,
)
def get_zone_records(output, id):
    r = lib.route53.get_records(id)
    if output == True and id == None:

        lib.file.write_yaml(r)
    elif output == True and id != None:
        lib.file.write_yaml(r, (r["zone_info"]["name"]).replace(".", "_dot_") + ".yaml")
    else:
        print(r)


if __name__ == "__main__":
    main()
