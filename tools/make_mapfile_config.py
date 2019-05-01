import re
import os
import sys
from warnings import warn
from glob import glob
import math
import json

map_file_dict = {'mapfiles': []}


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


def zoomlevel_for_scaledenom(scaledenom, domax=True):
    # scaledenom is denominator for scale (10000 means 1 cm is 10000 cm in reality)
    # zoomlevel is a log2 indication for the total number of pixels for the entire earth
    # See  : https://leafletjs.com/examples/zoom-levels/
    if scaledenom == 0:
        return 16  # max zoomlevel
    c = 10400000  # Constant to be able to compute acceptable zoomlevels
    zlf = math.log(c / scaledenom, 2)
    if domax:
        zoomlevel = int(math.ceil(zlf))
    else:
        zoomlevel = int(math.floor(zlf))
    return 16 if zoomlevel >= 16 else 8 if zoomlevel <= 8 else zoomlevel


def scan_map_file(mapfile):

    eprint(f'Processing {mapfile}...')
    s = mapfile.rfind('/')
    if s > 0:
        name = mapfile[s+1:-4]
    else:
        name = mapfile[:-4]

    # print(name)
    cur_map_file = {
        'file_name': name,
        'layers': []
    }

    cur_layer = None
    cur_class = None

    map_file_dict['mapfiles'].append(cur_map_file)
    state = []
    dict_stack = []
    element = re.compile(r'"[^"]*"|\S+')
    comment = re.compile(r'\s*#')
    ws = re.compile(r'(\s+)')
    count = 0
    try:
        with open(mapfile, encoding='utf-8') as file:
            for line in file:
                count += 1
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
                    if expected is not None and len(state) == 0:
                        print(expected)
                    elif (expected is None and len(state) == 0) or (
                            type(expected) == list and state[-1] in expected) or expected == state[-1]:
                        state.append(elements[0])
                        if state[-1] in name_elements:
                            dict_stack.append('NEW_UNKOWN_NAME')
                            # print(dict_stack)
                            if state[-1] == 'LAYER':
                                cur_layer = {'classes': []}
                                cur_map_file['layers'].append(cur_layer)
                            elif state[-1] == 'CLASS':
                                assert cur_layer is not None
                                cur_class = {}
                                cur_layer['classes'].append(cur_class)
                    elif elements[0] == 'SYMBOL' and len(elements) > 1:
                        # Process symbol
                        pass
                    else:
                        raise Exception(f"Invalid {elements[0]} in {mapfile} line {count}")
                elif elements[0] == 'END':
                    if len(state) > 0:
                        if state[-1] in name_elements and len(dict_stack) > 0:
                            dict_stack.pop()
                            if state[-1] == 'CLASS':
                                cur_class = None
                            elif state[-1] == 'LAYER':
                                cur_layer = None
                        state.pop()
                    else:
                        warn(f"Invalid {elements[0]} in {mapfile} line {count}")
                # Process elements here
                if elements[0] == 'NAME' and state[-1] in name_elements:
                    name = elements[1].strip('"').strip("'")
                    if state[-1] == 'CLASS':
                        cur_class['name'] = name
                    elif state[-1] == 'LAYER':
                        cur_layer['name'] = name
                    elif state[-1] == 'MAP':
                        cur_map_file['name'] = name
                elif elements[0] == 'GROUP' and state[-1] == 'LAYER':
                    group = elements[1].strip('"')
                    layer = dict_stack[-1]
                    my_stack = dict_stack[0:-1]
                elif elements[0] == 'MINSCALEDENOM' and state[-1] == 'LAYER':
                    max_zoom = zoomlevel_for_scaledenom(int(elements[1]), False)
                    cur_layer['maxZoom'] = max_zoom
                elif elements[0] == 'MAXSCALEDENOM' and state[-1] == 'LAYER':
                    min_zoom = zoomlevel_for_scaledenom(int(elements[1]), True)
                    cur_layer['minZoom'] = min_zoom

                # In one case the END is on the line itself
                if len(elements) > 1 and elements[-1] == 'END':
                    popped = state.pop()
    except UnicodeDecodeError as e:
        eprint(f"Error {e} at {mapfile} {count}")


def main():
    current_dir = os.getcwd()
    script_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_dir)

    public_mapfiles = glob('../*.map')
    mapfiles = list(public_mapfiles)
    if os.getenv('ACCESS_SCOPE', 'public') == 'private':
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
