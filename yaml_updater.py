"""
This is a python script to modify swagger api yaml file.
updating objects containing "$ref" keys in the yaml file with corresponding objects in "$ref" path.
Eg:
        - $ref: '#/paths/~1tours/get/parameters/2'
 here this script will remove the parent object containing "$ref" and replace it
 with the object specified in path string.
Requirements:
-------------
=> yaml module must be installed.
=> change input and output file names accordingly
"""

import yaml
import sys

input_file = "swagger_api.yaml"
output_file = "output.yaml"
ref_counter = 0
data = None
data_bkp = None


def get_object_from_path_list(path_list):
    var_obj = data_bkp
    for path in path_list:
        if isinstance(var_obj, dict):
            var_obj = var_obj[str(path)]
        elif isinstance(var_obj, list):
            var_obj = var_obj[int(path)]
    # print(var_obj)
    return var_obj


def get_object_from_path(path):
    path_list = path.split("/")
    # removing '#' from beginning
    path_list.pop(0)
    for index in range(len(path_list)):
        # replacing "~1" with "/"
        path_list[index] = path_list[index].replace("~1", "/")
    return get_object_from_path_list(path_list)


def traverse_tree(obj):
    """
    This is  a recursive function which will traverse through the dictionary or list "obj"
    and will replace any object having "$ref" as key with corresponding object in the reference path
    :param obj: any object
    :return: if "$ref" found as key in an object then object in the referenced path will be returned otherwise None.
    """
    if isinstance(obj, dict):
        ref_path_obj = None
        for key, value in obj.items():
            if key == "$ref":
                global ref_counter
                ref_counter += 1
                # print(f"{ref_counter}. {key}:{value}")
                ref_path_obj = get_object_from_path(value)
                break
            else:
                return_value = traverse_tree(value)
                if return_value is not None:
                    # if this "value" object having any "$ref" as its key then object of that reference path is assigned
                    obj[key] = return_value
        if ref_path_obj is not None:
            # here we are returning the object value of "$ref" to calling recursive function
            return ref_path_obj
    elif isinstance(obj, list):
        for j in range(len(obj)):
            return_value = traverse_tree(obj[j])
            if return_value is not None:
                # if this obj[j] having any "$ref" as its key then object of that reference path is assigned
                obj[j] = return_value


if __name__ == '__main__':
    '''main function'''
    # change recursion limit for large files
    # sys.setrecursionlimit(10000)

    with open(input_file) as ip_file:
        data = yaml.safe_load(ip_file)
    # data_bkp is used to replace references
    data_bkp = data
    ref_counter = 0
    traverse_tree(data)
    print("\n\nref_counter=============" + str(ref_counter))
    # saving to output file
    with open(output_file, "w") as op_file:
        # this configuration is needed for proper output without object aliases
        yaml.Dumper.ignore_aliases = lambda *args: True
        yaml.dump(data, op_file)
