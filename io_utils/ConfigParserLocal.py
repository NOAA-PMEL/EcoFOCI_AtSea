"""
 Background:
 --------
 ConfigParserLocal.py
 
 
 Purpose:
 --------
 Parse mooring specific and EcoFOCI specific configuration files for various routines

 The .pyini files are JSON formatted
 The .yaml files are YAML formatted

 Modifications:
 --------------

 2019-05-29: SW Bell - subroutine to order load in from yaml file
    https://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-mappings-as-ordereddicts
 2018-06-14: SW Bell - make python3 compliant
 2017-09-14: SW Bell - merge yaml and pyini(json) calls to unify api
 2016-09-16: SW Bell - Add support for parsing yaml files and translating between yaml and json/pyini
  

"""

# System Stack
import json
import yaml

from collections import OrderedDict


def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping
    )
    return yaml.load(stream, OrderedLoader)


def get_config(infile, ftype="yaml"):
    """ Input - full path to config file
    
        Output - dictionary of file config parameters
    """
    infile = str(infile)

    if ftype in ["json", "pyini"]:
        try:
            d = json.load(open(infile))
        except:
            raise RuntimeError("{0} not found".format(infile))
    elif ftype in ["yaml"]:
        try:
            d = ordered_load(open(infile))
        except:
            raise RuntimeError("{0} not found".format(infile))
    else:
        raise RuntimeError("{0} format not recognized".format(infile))

    return d


def write_config(infile, data, ftype="yaml"):
    """ Input - full path to config file
        Dictionary of parameters to write
        
        Output - None
    """
    infile = str(infile)

    if ftype in ["json", "pyini"]:
        try:
            data = json.dump(data, open(infile, "w"), sort_keys=True, indent=4)
        except:
            raise RuntimeError("{0} not found".format(infile))
    elif ftype in ["yaml"]:
        try:
            data = yaml.safe_dump(data, open(infile, "w"), default_flow_style=False)
        except:
            raise RuntimeError("{0} not found".format(infile))
    else:
        raise RuntimeError("{0} format not recognized".format(infile))


def pyini2yaml(infile, default_flow_style=False):
    """ Input - full path to config file
    
        Output - dictionary of file config parameters
    """
    infile = str(infile)

    try:
        d = yaml.safe_dump(
            json.load(open(infile)), default_flow_style=default_flow_style
        )

    except:
        raise RuntimeError("{0} not found".format(infile))

    return d


def yaml2pyini(infile, **kwargs):
    """ Input - full path to config file
    
        Output - dictionary of file config parameters
    """
    infile = str(infile)

    try:
        d = json.dumps(ordered_load(open(infile)), **kwargs)

    except:
        raise RuntimeError("{0} not found".format(infile))

    return d


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Convert yaml to json or json to yaml")
    parser.add_argument(
        "config_file",
        metavar="config_file",
        type=str,
        help="full path of file to be converted",
    )

    args = parser.parse_args()

    print(args.config_file)

    if (args.config_file).split(".")[-1] in ["pyini", "json"]:
        print(pyini2yaml(args.config_file))
    elif (args.config_file).split(".")[-1] == "yaml":
        print(yaml2pyini(args.config_file, sort_keys=True, indent=4))
    else:
        print("only pyini and yaml endings are accepted")


if __name__ == "__main__":
    main()
