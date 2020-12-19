from bokeh.layouts import column, gridplot, layout
from bokeh.models import Div
from bokeh.models.callbacks import CustomJS
from bokeh.models.widgets import Slider
from bokeh.plotting import output_file, show

import plots
import constants
import datasources

# Set up widgets
sma = Slider(
    title="a: semi-major axis (km)",
    value=42164,
    start=0,
    end=constants.MAX_SMA,
    step=10,
    css_classes=["sma_slider"],
)
eccentricity = Slider(title="eccentricity (-)", value=0.7, start=0, end=1, step=0.01)
aop = Slider(
    title="ω: argument of perigee (deg)",
    value=0,
    start=0,
    end=360,
    step=1,
    css_classes=["omega_slider"],
)
inclination = Slider(title="inclination (deg)", value=0, start=0, end=180, step=1)
raan = Slider(
    title="right ascension of ascending node (deg)",
    value=0,
    start=0,
    end=360,
    step=1,
    css_classes=["Gomega_slider"],
)
anomaly = Slider(
    title="𝜈: true anomaly (deg)",
    value=0,
    start=0,
    end=359,
    step=1,
    css_classes=["anomaly_slider"],
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
    sma,
    eccentricity,
    aop,
    inclination,
    raan,
    anomaly,
    sizing_mode="stretch_width",
)
plots = gridplot(
    [[inputs, plot_vernal, plot_xz], [plot_shape, orbit_description_div, plot_pole]],
    toolbar_options=dict(logo=None),
)
style = Div(text="<LINK href='style.css' rel='stylesheet' type='text/css'>")
intro = Div(
    text="""
<h1>Orbital Parameters Visualization</h1>
<p>Manipulate the sliders to change the keplerian orbit parameters,
 and see how they affect the orbit in real time.</p>
<p>When the orbit trajectory is represented by a thick line,
 it means that it is above the plane of the screen.</p>
""",
    sizing_mode="stretch_width",
)
footnote = Div(
    align="center",
    text="""
    <a href="https://github.com/jyannick/orbital-parameters">
        View project page on GitHub
    </a>
    """,
)

output_file("index.html", title="Orbital Parameters Visualization")
show(layout(style, intro, plots, footnote))
