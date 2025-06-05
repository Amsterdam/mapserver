import os
import requests
import xml.etree.ElementTree as ET

# ✅ Base URL pattern for your MapServer instance
#BASE_URL = "http://localhost:8383/maps"
BASE_URL = "https://map.data.amsterdam.nl/maps"

# ✅ Automatically use the same directory as the script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAPFILES_DIR = SCRIPT_DIR


def get_mapfiles(directory):
    """Find all .map files in the directory tree."""
    mapfiles = []
    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith(".map"):
                mapfiles.append(os.path.join(root, f))
    return mapfiles


def check_geometry_present(base_url, typename):
    """Do a WFS GetFeature request and check if a geometry exists."""
    params = {
        "SERVICE": "WFS",
        "VERSION": "2.0.0",
        "REQUEST": "GetFeature",
        "TYPENAME": typename,
        "COUNT": 1,
        "OUTPUTFORMAT": "application/gml+xml; version=3.2"
    }
    try:
        response = requests.get(base_url, params=params, timeout=5)
        response.raise_for_status()
        root = ET.fromstring(response.content)

        # Dynamically get the GML namespace
        nsmap = {
            k if k else 'gml': v
            for k, v in root.attrib.items()
            if v.startswith("http://www.opengis.net/gml")
        }

        # Search for any known geometry tag
        for elem in root.iter():
            tag = elem.tag.lower()
            if any(geom in tag for geom in ["polygon", "point", "linestring", "surface", "geometry"]):
                return True

        # Fallback: check for boundedBy as minimal geometry presence
        for elem in root.iter():
            if "boundedby" in elem.tag.lower():
                return True

        return False
    except Exception as e:
        print(f"   ⚠️ Error checking geometry for {typename}: {e}")
        return False


def get_wfs_layers(mapfile_path):
    """Query WFS GetCapabilities and check each layer for geometry."""
    mapname = os.path.splitext(os.path.basename(mapfile_path))[0]
    base_url = f"{BASE_URL}/{mapname}"
    capabilities_url = f"{base_url}?SERVICE=WFS&VERSION=2.0.0&REQUEST=GetCapabilities"

    try:
        response = requests.get(capabilities_url, timeout=5)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        namespaces = {'wfs': 'http://www.opengis.net/wfs/2.0'}
        layers = []

        for ft in root.findall('.//wfs:FeatureType', namespaces):
            name_elem = ft.find('wfs:Name', namespaces)
            title_elem = ft.find('wfs:Title', namespaces)
            typename = name_elem.text if name_elem is not None else None
            title = title_elem.text if title_elem is not None else "(no title)"

            has_geometry = check_geometry_present(base_url, typename) if typename else False

            layers.append({
                "name": typename,
                "title": title,
                "geometry": has_geometry
            })

        return layers

    except Exception as e:
        print(f"❌ Failed to read WFS from {mapname}: {e}")
        return []


def main():
    mapfiles = get_mapfiles(MAPFILES_DIR)
    for m in mapfiles:
        print(f"\n🗂️ Mapfile: {m}")
        layers = get_wfs_layers(m)
        if layers:
            for layer in layers:
                status = "✅ geometry found" if layer["geometry"] else "❌ no geometry"
                print(f"  - {layer['title']} [{layer['name']}] — {status}")
        else:
            print("  ⚠️ No WFS layers found or error parsing.")


if __name__ == "__main__":
    main()