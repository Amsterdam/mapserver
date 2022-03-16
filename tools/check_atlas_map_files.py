import re
import os
from warnings import warn
from glob import glob
from functools import reduce
import operator
import math
import yaml
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
    'STYLE': 'CLASS',
    'LABEL': 'CLASS',
    'PATTERN': 'STYLE',
}

name_elements = ('MAP', 'LAYER', 'CLASS')


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


def check_map_panel_layers():
    filename = '../../atlas/src/map/services/map-panel-layers/map-panel-layers.js'
    with open(filename) as file:
        print(f"Processing {filename}...")
        panel_layers = file.read()
        if panel_layers[:15] == 'export default ':
            panel_layers = panel_layers[15:]
        panel_layers = panel_layers.strip('\n').strip(';')
        eq = re.compile(r"\'([^'\\]*)\\'([^'\\]*)\\'([^'\\]*)\'", re.VERBOSE)
        panel_layers = eq.sub(r"\"\1'\2'\3\"", panel_layers)
        eq = re.compile(r"\'([^'\\]*)\\'([^'\\]*)\'", re.VERBOSE)
        panel_layers = eq.sub(r"\"\1'\2\"", panel_layers)
        panel_layers_json = yaml.load(panel_layers)
        for item in panel_layers_json:
            stop_item = False
            selected_layer = None
            if 'title' in item:
                print(f"Check {item['title']}")
            if 'url' in  item:
                url = item['url']
                m = re.match(r'/maps/([^\?]*)\?version=1\.3\.0\&service=WMS', url)
                if m:
                    mapfile = m.group(1)
                    if mapfile not in map_file_dict:
                        warn(f"Missing mapfile {mapfile} in map-panel-layers.js")
                    (map_name, map_value) = list(map_file_dict[mapfile].items())[0]

                    if 'layers' in item:
                        layers = item['layers']
                        for layer in layers:
                            if layer not in map_value and not (GROUPS_NAME in map_value and layer in map_value[GROUPS_NAME]):
                                warn(f"Missing layer {layer} for {mapfile} in map-panel-layers.js")
                                stop_item = True

                        if len(layers) == 1:
                            selected_layer = layers[0]
                    if stop_item:
                        continue
                    if 'legendItems' in item:
                        legend_items = item['legendItems']
                        for legend_item in legend_items:
                            li_title = legend_item['title']
                            li_title = li_title.strip('\\"')
                            selectable = item['selectable'] if 'selectable' in item else False
                            if 'layer' in legend_item:
                                layer_li = legend_item['layer']
                                if isinstance(layer_li, list):
                                    layer_li = layer_li[0]
                                    warn(f"legendItem {li_title} contains list of layer {layer_li} in map-panel-layers.js")
                                if layer_li not in map_value:
                                    warn(f"Missing layer {layer_li} for legendItem {li_title} in map-panel-layers.js")
                            elif selected_layer is not None:
                                layer_li = selected_layer
                            else:
                                warn("Missing or unknown layer for legendItem {li_title}")
                            if selectable:
                                pass
                            else:
                                # Check class name in dict
                                if layer_li not in map_value:
                                    if GROUPS_NAME in map_value and layer_li in map_value[GROUPS_NAME]:
                                        layer_li = map_value[GROUPS_NAME][layer_li]
                                    else:
                                        warn(f"Missing layer {layer_li} in map {mapfile} in map-panel-layers.js")
                                        continue
                                layers_li = layer_li if isinstance(layer_li, list) else [layer_li]
                                found_in_layer = list(filter(lambda x: li_title in map_value[x], layers_li))
                                if len(found_in_layer) == 0:
                                    warn(f"Missing class name {li_title} for layer {layer_li}, map {mapfile} in map-panel-layers.js")

                else:
                    continue


def main():
    current_dir = os.getcwd()
    script_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_dir)

    public_mapfiles = glob('../*.map')
    private_mapfiles = glob('../private/*.map')
    mapfiles = list(public_mapfiles)
    mapfiles.extend(private_mapfiles)

    for mapfile in mapfiles:
        if re.search(r'lufo', mapfile):
            continue
        scan_map_file(mapfile)

    # print(json.dumps(map_file_dict, indent=4, sort_keys=True))
    check_map_panel_layers()

    os.chdir(current_dir)


if __name__ == '__main__':
    main()