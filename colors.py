import re


def read_css_variables(filename):
    with open(filename) as f:
        colors = {
            match.group(1): match.group(2)
            for match in re.finditer(r"--(.*): ?(.*);", f.read())
        }
    return colors


def substitute_variables(colors):
    for k, v in colors.items():
        match = re.match(r"var\(--(.*)\)", v)
        if match:
            colors[k] = colors[match.group(1)]
    return colors


colors = substitute_variables(read_css_variables("colors.css"))
