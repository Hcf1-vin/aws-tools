import lib.profile

r53_client = lib.profile.create_sesssion(client_name="route53")


def get_zones():

    paginator = r53_client.get_paginator("list_hosted_zones")
    hosted_zones = list()
    response_iterator = paginator.paginate()
    for a in response_iterator:
        hosted_zones = hosted_zones + a["HostedZones"]

    return hosted_zones


def get_zone_info(zone_id):

    response = r53_client.get_hosted_zone(Id=zone_id)
    zone_info = {}
    vpc_list = []

    zone_info["name"] = response["HostedZone"]["Name"]
    zone_info["private"] = response["HostedZone"]["Config"]["PrivateZone"]
    zone_info["record_count"] = response["HostedZone"]["ResourceRecordSetCount"]

    if zone_info["private"] == True:
        for a in response["VPCs"]:
            vpc_list.append(a["VPCId"])

    zone_info["vpc_list"] = vpc_list

    return zone_info


def get_records(zone_id=None):

    zone_ids = get_zones()

    zone_list = list()
    if zone_id == None:
        for zone in zone_ids:
            zone_dict = dict()
            zone_dict["zone"] = dict()
            zone_dict["zone"]["zone_info"] = get_zone_info(zone["Id"])
            zone_dict["zone"]["records"] = paginate_records(zone["Id"])
            zone_list.append(zone_dict)
    elif zone_id not in str(zone_ids):
        raise Exception(f"{zone_id} not found")
    else:
        zone_id = "/hostedzone/" + zone_id
        zone_dict = dict()

        zone_dict["zone_info"] = get_zone_info(zone_id)
        zone_dict["records"] = paginate_records(zone_id)
        return zone_dict

    return zone_list


def paginate_records(zone_id):

    is_truncated = True
    marker = None
    record_list = []
    while is_truncated != False:
        if marker == None:
            response = r53_client.list_resource_record_sets(HostedZoneId=zone_id)
        else:
            response = r53_client.list_resource_record_sets(
                HostedZoneId=zone_id, StartRecordName=marker,
            )
        if "NextRecordName" in response:
            marker = response["NextRecordName"]
        else:
            marker = None

        if "IsTruncated" in response:
            is_truncated = response["IsTruncated"]
        else:
            is_truncated = False

        for a in response["ResourceRecordSets"]:

            record_dict = {}
            if a["Type"] == "A" or a["Type"] == "CNAME":
                record_value = []
                record_dict["name"] = a["Name"]

                if "AliasTarget" in a:
                    record_dict["type"] = "CNAME"
                    record_value.append(a["AliasTarget"]["DNSName"])
                else:
                    record_dict["type"] = a["Type"]
                    for b in a["ResourceRecords"]:
                        record_value.append(b["Value"])

                record_dict["value"] = record_value
                record_list.append(record_dict)

    return record_list
