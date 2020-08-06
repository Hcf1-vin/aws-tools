import os
import csv
import sys
import yaml
from datetime import datetime
from jinja2 import Environment, FileSystemLoader


def output_dir():
    print(sys.path[0])
    output_director = os.path.join(sys.path[0], "outputs")

    if not os.path.exists(output_director):
        os.makedirs(output_director)

    return output_director


def write_csv(data):

    output_file = os.path.join(output_dir(), (random_file_name() + ".csv"))
    keys = data[0].keys()

    with open(output_file, "w") as csv_file:
        dict_writer = csv.DictWriter(csv_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

    print(f"Your file can be found here -> {output_file}")


def write_yaml(data, filename=None):
    if filename == None:
        filename = str(random_file_name() + ".yaml")
    data_yaml = yaml.dump(data)
    file_path = os.path.join(output_dir(), filename)
    write_file(data_yaml, file_path)


def random_file_name():
    return datetime.today().strftime("%Y%m%d%H%M%S")


def render_template(data, template_file):

    file_loader = FileSystemLoader(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates")
    )
    env = Environment(loader=file_loader)
    template = env.get_template(template_file)
    output = template.render(data=data)
    return output


def write_file(data, file_path):
    f = open(file_path, "w+")
    f.write(data)
    f.close()

