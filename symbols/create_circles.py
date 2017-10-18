colors = [
    (241, 119, 48),
    (250, 178, 49),
    (254, 239, 53),
    (183, 210, 66),
    (97, 184, 77),
    (23, 164, 84),
    (26, 170, 182),
    (29, 174, 236),
    (21, 134, 201),
    (13, 97, 171),
    (47, 52, 144),
    (117, 47, 142),
    (233, 22, 139),
]


svg_dashed = """
<svg width="40" height="40">
<circle cx="20" cy="20" r="10" stroke="black" stroke-width="4" stroke-dasharray="5, 2" fill="{}" fill-opacity="0.4"/>
</svg>
"""

for i, color in enumerate(colors):
    file_name = "stipdash{}.svg".format(i+1)
    with open(file_name, 'w') as svg:
        rgb = 'rgb({},{},{})'.format(*color)
        data = svg_dashed.format(rgb)
        svg.write(data)
