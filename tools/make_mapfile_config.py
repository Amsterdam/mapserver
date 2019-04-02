import re
import os
import sys
from warnings import warn
from glob import glob
from functools import reduce
import operator
import math
import json

GROUPS_NAME = '__groups__'
TYPE_NAME = '__type__'

map_file_dict = {}


expected_state = {
    'MAP': None,
    'LAYER': 'MAP',
    'PROJECTION': 'LAYER',
    'WEB': 'MAP',
    'OUTPUTFORMAT': 'MAP',
    'SYMBOL': 'MAP',
    'LEGEND': 'MAP',
    'POINTS': 'SYMBOL',
    'METADATA': ['LAYER', 'WEB'],
    'CLASS': 'LAYER',
    'COMPOSITE': 'LAYER',
    'VALIDATION': 'LAYER',
    'STYLE': ['CLASS', 'LABEL'],
    'LABEL': 'CLASS',
    'PATTERN': 'STYLE',
}

name_elements = ('MAP', 'LAYER', 'CLASS')


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_from_dict(datadict, maplist):
    return reduce(operator.getitem, maplist, datadict)


def set_in_dict(datadict, maplist, value):
    get_from_dict(datadict, maplist[:-1])[maplist[-1]] = value


def add_to_dict(datadict, maplist, key, value):
    get_from_dict(datadict, maplist)[key] = value


def replace_key_in_dict(datadict, maplist, new_key):
    d = get_from_dict(datadict, maplist[:-1])
    d[new_key] = d.pop(maplist[-1])
    maplist[-1] = new_key


def zoomlevel_for_scaledenom(scaledenom, domax=True):
    if scaledenom == 0:
        return 16  # max zoomlevel
    C = 10400000  # TODO determine exactly
    zlf = math.log(C / scaledenom, 2)
    if domax:
        zoomlevel = int(math.ceil(zlf))
    else:
        zoomlevel = int(math.floor(zlf))
    return 16 if zoomlevel >= 16 else 8 if zoomlevel <= 8 else zoomlevel


def scan_map_file(mapfile):
    s = mapfile.rfind('/')
    if s > 0:
        name = mapfile[s+1:-4]
    else:
        name = mapfile[:-4]
    # print(name)
    map_file_dict[name] = {}
    cur_dict = map_file_dict[name]
    state = []
    dict_stack = []
    element = re.compile(r'"[^"]*"|\S+')
    comment = re.compile(r'\s*#')
    ws = re.compile(r'(\s+)')
    count = 0
    try:
        with open(mapfile) as file:
            for line in file:
                count+=1
                pos = line.find('#')
                if pos == 0:
                    continue
                elif pos > 0:
                    line = line[0:pos-1]

                if comment.match(line):
                    continue
                m = ws.match(line)
                if m:
                    ws_count = len(m.group(1))
                else:
                    ws_count = 0
                elements = element.findall(line)
                if len(elements) == 0:
                    continue
                # print(ws_count, elements)
                if elements[0] in expected_state:
                    expected = expected_state[elements[0]]
                    if (expected is None and len(state) == 0) or (
                            type(expected) == list and state[-1] in expected) or expected == state[-1]:
                        state.append(elements[0])
                        if state[-1] in name_elements:
                            dict_stack.append('NEW_UNKOWN_NAME')
                            # print(dict_stack)
                            set_in_dict(cur_dict, dict_stack, {TYPE_NAME: state[-1]})
                        # print(state)
                    elif elements[0] == 'SYMBOL' and len(elements) > 1:
                        # Process symbol
                        pass
                    else:
                        raise Exception(f"Invalid {elements[0]} in {mapfile} line {count}")
                elif elements[0] == 'END':
                    if len(state) > 0:
                        if state[-1] in name_elements and len(dict_stack) > 0:
                            dict_stack.pop()
                        state.pop()
                        # print(dict_stack)
                    else:
                        warn(f"Invalid {elements[0]} in {mapfile} line {count}")
                # Process elements here
                if elements[0] == 'NAME' and state[-1] in name_elements:
                    name = elements[1].strip('"').strip("'")
                    replace_key_in_dict(cur_dict, dict_stack, name)
                elif elements[0] == 'GROUP' and state[-1] == 'LAYER':
                    group = elements[1].strip('"')
                    layer = dict_stack[-1]
                    my_stack = dict_stack[0:-1]
                    d = get_from_dict(cur_dict, my_stack)
                    if GROUPS_NAME in d:
                        if group in d[GROUPS_NAME]:
                            d[GROUPS_NAME][group].append(layer)
                        else:
                            d[GROUPS_NAME][group] = [layer]
                    else:
                        d[GROUPS_NAME] = {group: [layer]}
                elif elements[0] == 'MINSCALEDENOM' and state[-1] == 'LAYER':
                    maxZoom = zoomlevel_for_scaledenom(int(elements[1]), False)
                    add_to_dict(cur_dict, dict_stack, 'maxZoom', maxZoom)
                elif elements[0] == 'MAXSCALEDENOM' and state[-1] == 'LAYER':
                    minZoom = zoomlevel_for_scaledenom(int(elements[1]), True)
                    add_to_dict(cur_dict, dict_stack, 'minMoom', minZoom)

                # In one case the END is on the line itself
                if len(elements) > 1 and elements[-1] == 'END':
                    popped = state.pop()
                    # print(state)
    except UnicodeDecodeError as e:
        eprint(f"Error {e} at {mapfile} {count}")


def main():
    current_dir = os.getcwd()
    script_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_dir)

    public_mapfiles = glob('../*.map')
    mapfiles = list(public_mapfiles)
    if os.getenv('ACCESS_SCOPE','public') == 'private':
        private_mapfiles = glob('../private/*.map')
        mapfiles.extend(private_mapfiles)

    for mapfile in mapfiles:
        if re.search(r'lufo', mapfile):
            continue
        scan_map_file(mapfile)

    print(json.dumps(map_file_dict, indent=4, sort_keys=True))

    os.chdir(current_dir)


if __name__ == '__main__':
    main()