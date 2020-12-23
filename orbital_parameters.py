from bokeh.layouts import column, gridplot, layout
from bokeh.models import Div, Button
from bokeh.models.callbacks import CustomJS

from bokeh.plotting import save, output_file
from jinja2 import Environment, FileSystemLoader

import plots
import constants
import datasources
import widgets

# Set up widgets
sma_widget, sma = widgets.build_orbital_parameter(
    title="a: semi-major axis (km)",
    value=42164,
    start=0,
    end=constants.MAX_SMA,
    step=1,
    css_class="sma",
)
eccentricity_widget, eccentricity = widgets.build_orbital_parameter(
    title="e: eccentricity (-)",
    value=0.7,
    start=0,
    end=1,
    step=0.01,
    css_class="ecc",
)
aop_widget, aop = widgets.build_orbital_parameter(
    title="ω: argument of perigee (deg)",
    value=195,
    start=0,
    end=360,
    step=1,
    css_class="omega",
)
inclination_widget, inclination = widgets.build_orbital_parameter(
    title="i: inclination (deg)",
    value=10,
    start=0,
    end=180,
    step=1,
    css_class="inc",
)
raan_widget, raan = widgets.build_orbital_parameter(
    title="Ω: right ascension of ascending node (deg)",
    value=95,
    start=0,
    end=360,
    step=1,
    css_class="Gomega",
)
anomaly_widget, anomaly = widgets.build_orbital_parameter(
    title="𝜈: true anomaly (deg)",
    value=70,
    start=0,
    end=359,
    step=1,
    css_class="anomaly",
)


plot_shape = plots.create_plot(
    datasources.orbit_shape,
    "x",
    "y",
    "+z",
    datasources.position_in_orbital_plane,
    "orbit shape in orbital plane",
)
plots.add_ascending_node_direction(plot_shape)
plots.add_apsides_line(plot_shape, datasources.apsides_in_orbital_plane)
plots.add_sma(plot_shape, datasources.orbital_parameters)
plots.add_eccentricity(plot_shape, datasources.orbital_parameters)
plots.add_omega(plot_shape, datasources.orbital_parameters)
plots.add_anomaly(
    plot_shape, datasources.orbital_parameters, datasources.position_in_orbital_plane
)

plot_pole = plots.create_plot(
    datasources.orbit_3d,
    "x",
    "y",
    "+z",
    datasources.position_3d,
    "orbit seen from North direction",
)
plots.add_vernal_direction(plot_pole)
plots.add_Gomega(plot_pole, datasources.orbital_parameters)
plots.add_nodes_line(plot_pole, datasources.nodes_in_equatorial_plane)
plots.add_equatorial_plane(plot_pole)

plot_vernal = plots.create_plot(
    datasources.orbit_3d,
    "y",
    "z",
    "+x",
    datasources.position_3d,
    "orbit seen from Vernal equinox",
)
plots.add_north_direction(plot_vernal)
plots.add_equator_line(plot_vernal)

plot_xz = plots.create_plot(
    datasources.orbit_3d, "x", "z", "-y", datasources.position_3d, ""
)
plots.add_north_direction(plot_xz)
plots.add_vernal_direction(plot_xz)
plots.add_equator_line(plot_xz)

# Set up callbacks
with open("callback.js", "r") as f:
    sliders_callback_code = f.read()

orbit_description_div = Div(
    css_classes=["orbit-description"],
    text="""
<h2>Orbital Data</h2>
<p>Please manipulate the sliders to update this data.</p>
""",
)


callback_args = dict(
    orbit_shape=datasources.orbit_shape,
    orbit_3d=datasources.orbit_3d,
    position_in_orbital_plane=datasources.position_in_orbital_plane,
    position_3d=datasources.position_3d,
    apsides_in_orbital_plane=datasources.apsides_in_orbital_plane,
    nodes_in_equatorial_plane=datasources.nodes_in_equatorial_plane,
    sma=sma,
    eccentricity=eccentricity,
    aop=aop,
    inclination=inclination,
    raan=raan,
    anomaly=anomaly,
    N=datasources.N,
    orbit_description_div=orbit_description_div,
    orbital_parameters=datasources.orbital_parameters,
)

for w in [sma, eccentricity, aop, inclination, raan, anomaly]:
    w.js_on_change("value", CustomJS(args=callback_args, code=sliders_callback_code))

# Set up layouts and add to document
inputs = column(
    Div(text="<h2>Orbital Parameters</h2>"),
    sma_widget,
    eccentricity_widget,
    inclination_widget,
    aop_widget,
    raan_widget,
    anomaly_widget,
    sizing_mode="stretch_width",
    height=400,
    css_classes=["inputs"],
)
plots = gridplot(
    [[inputs, plot_vernal, plot_xz], [plot_shape, orbit_description_div, plot_pole]],
    toolbar_options=dict(logo=None),
)
intro = Div(
    text="""
<h1>Orbit Visualization</h1>
<p>When the orbit trajectory is represented by a thick line,
 it means that it is above the plane of the screen.</p>
""",
    sizing_mode="stretch_width",
)

button = Button(label="Update", css_classes=["update_button"], width=1, height=1)
button.js_on_click(CustomJS(args=callback_args, code=sliders_callback_code))

_env = Environment(loader=FileSystemLoader("templates"))
output_file("index.html")
save(
    layout(intro, button, plots),
    title="Orbital Parameters Visualization",
    template=_env.get_template("template.html.j2"),
)
