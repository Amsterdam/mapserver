from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import re

# Configure your MapServer layers here
LAYERS = {
    "water":   ("http://localhost:8383/maps/water",  "binnenwater"),
    "nap":     ("http://localhost:8383/maps/nap",    "peilmerk"),
}

PORT = 8080

class MVTProxy(BaseHTTPRequestHandler):
    def do_GET(self):
        # Expects: /{layername}/{z}/{x}/{y}.mvt
        m = re.match(r"/(\w+)/(\d+)/(\d+)/(\d+)\.mvt", self.path)
        if not m:
            self.send_error(404, "Use format: /{layername}/{z}/{x}/{y}.mvt")
            return

        name, z, x, y = m.groups()

        if name not in LAYERS:
            self.send_error(404, f"Unknown layer '{name}'. Available: {list(LAYERS.keys())}")
            return

        mapserver_url, layer = LAYERS[name]
        url = (f"{mapserver_url}?MODE=tile&TILEMODE=gmap"
               f"&TILE={x}+{y}+{z}&LAYERS={layer}&map.imagetype=mvt")

        try:
            with urllib.request.urlopen(url) as r:
                data = r.read()
        except Exception as e:
            self.send_error(502, str(e))
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/vnd.mapbox-vector-tile")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        print(f"{self.path} -> {args[1]}")

print(f"MVT proxy running on http://localhost:{PORT}")
print("QGIS URLs:")
for name in LAYERS:
    print(f"  {name}: http://localhost:{PORT}/{name}/{{z}}/{{x}}/{{y}}.mvt")

HTTPServer(("", PORT), MVTProxy).serve_forever()
