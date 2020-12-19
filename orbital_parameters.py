import numpy as np

from bokeh.layouts import column, gridplot, layout
from bokeh.models import ColumnDataSource, Band, Div, LabelSet
from bokeh.models.callbacks import CustomJS
from bokeh.models.widgets import Slider
from bokeh.plotting import figure, output_file, show
from bokeh.models.annotations import Arrow, Label, Span
from bokeh.models.arrow_heads import VeeHead
from bokeh.models.filters import CustomJSFilter
from bokeh.models.sources import CDSView

NORTH_ARROW_COLOR = "rgb(35, 49, 245)"
VERNAL_ARROW_COLOR = "rgb(8, 94, 71)"
ORBIT_COLOR = "rgb(84, 227, 220)"
SMA_COLOR = "yellow"
OMEGA_COLOR = "orange"
GOMEGA_COLOR = "green"
V_COLOR = "red"

output_file("index.html", title="Orbital Parameters Visualization")
# Set up data
N = 180
Re = 6378  # km
max_sma = 50000  # km
plots_range = 80000  # km, half range
x = np.zeros(N)
y = np.zeros(N)
z = np.zeros(N)
orbit_shape = ColumnDataSource(data=dict(x=x, y=y, z=z))
position_in_orbital_plane = ColumnDataSource(data=dict(x=np.zeros(1), y=np.zeros(1)))
apsides_in_orbital_plane = ColumnDataSource(data=dict(x=np.zeros(2), y=np.zeros(2)))
nodes_in_equatorial_plane = ColumnDataSource(
    data=dict(x=np.zeros(2), y=np.zeros(2), labels=["asc. node", "desc. node"])
)
orbit_3d = ColumnDataSource(data=dict(x=x, y=y, z=z))
position_3d = ColumnDataSource(data=dict(x=np.zeros(1), y=np.zeros(1), z=np.zeros(1)))
orbital_parameters = ColumnDataSource(
    data=dict(
        a_x_start=np.zeros(1),
        a_x_end=np.zeros(1),
        a_y_start=np.zeros(1),
        a_y_end=np.zeros(1),
        a_label_x=np.zeros(1),
        a_label_y=np.zeros(1),
        a_text=["a"],
        e=np.zeros(1),
        i=np.zeros(1),
        omega=np.zeros(1),
        omega_label_x=np.zeros(1),
        omega_label_y=np.zeros(1),
        omega_text=["ω"],
        Gomega=np.zeros(1),
        Gomega_label_x=np.zeros(1),
        Gomega_label_y=np.zeros(1),
        Gomega_text=["Ω"],
        v_start=np.zeros(1),
        v_end=np.zeros(1),
        v_label_x=np.zeros(1),
        v_label_y=np.zeros(1),
        v_text=["𝜈"],
    )
)

t = np.linspace(0, np.pi, 10)
earth = ColumnDataSource(
    data=dict(x=Re * np.cos(t), upper=Re * np.sin(t), lower=-Re * np.sin(t))
)

# Set up widgets
sma = Slider(
    title="a: semi-major axis (km)",
    value=42164,
    start=0,
    end=max_sma,
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


def create_plot(source, x, y, depth, sat_position, title):
    depth_is_positive = depth.startswith("+")
    depth_coordinate = depth[1]
    plot = figure(
        plot_height=400,
        plot_width=400,
        title=title,
        match_aspect=True,
        aspect_scale=1,
        tools="",
        x_range=[-plots_range, plots_range],
        y_range=[-plots_range, plots_range],
        background_fill_color="rgb(32, 32, 32)",
        border_fill_color="rgb(40, 40, 40)",
        outline_line_alpha=0,
    )
    plot.title.text_color = "dodgerblue"
    plot.grid.visible = False
    plot.line(
        x,
        y,
        source=source,
        line_width=3,
        line_alpha=0.8,
        line_color=ORBIT_COLOR,
    )
    plot.line(
        x,
        y,
        source=source,
        view=generate_view(source, depth_coordinate, depth_is_positive),
        line_width=5,
        alpha=0.8,
        line_color=ORBIT_COLOR,
    )
    plot.circle_cross(x, y, source=sat_position, color="red", size=10, fill_alpha=0.2)
    plot.add_layout(
        Band(
            base="x",
            lower="lower",
            upper="upper",
            source=earth,
            level="underlay",
            fill_alpha=0.5,
            line_width=1,
            line_color="grey",
            fill_color="grey",
        )
    )
    return plot


def add_north_direction(plot):
    plot.add_layout(
        Arrow(
            end=VeeHead(
                size=10, fill_color=NORTH_ARROW_COLOR, line_color=NORTH_ARROW_COLOR
            ),
            line_width=3,
            x_start=0,
            y_start=0,
            x_end=0,
            y_end=plots_range,
            line_color=NORTH_ARROW_COLOR,
        )
    )
    plot.add_layout(
        Label(
            text="North",
            x=0.05 * plots_range,
            y=0.8 * plots_range,
            text_font_size="8pt",
            text_color=NORTH_ARROW_COLOR,
        )
    )


def add_vernal_direction(plot):
    plot.add_layout(
        Arrow(
            end=VeeHead(
                size=10, fill_color=VERNAL_ARROW_COLOR, line_color=VERNAL_ARROW_COLOR
            ),
            line_width=3,
            x_start=0,
            y_start=0,
            x_end=plots_range,
            y_end=0,
            line_color=VERNAL_ARROW_COLOR,
        )
    )
    plot.add_layout(
        Label(
            text="Vernal equinox",
            x=0.5 * plots_range,
            y=-0.1 * plots_range,
            text_font_size="8pt",
            text_color=VERNAL_ARROW_COLOR,
        )
    )


def add_ascending_node_direction(plot):
    plot.add_layout(
        Arrow(
            end=VeeHead(size=10),
            line_width=3,
            x_start=0,
            y_start=0,
            x_end=0.5 * plots_range,
            y_end=0,
        )
    )
    plot.add_layout(
        Label(
            text="ascending node",
            x=0.33 * plots_range,
            y=-0.03 * plots_range,
            text_font_size="8pt",
            text_color="grey",
        )
    )


def add_apsides_line(plot):
    plot.line(
        "x",
        "y",
        source=apsides_in_orbital_plane,
        line_width=3,
        line_alpha=0.3,
        color="grey",
    )


def add_nodes_line(plot):
    plot.line(
        "x",
        "y",
        source=nodes_in_equatorial_plane,
        line_width=3,
        line_alpha=0.3,
        color="grey",
    )
    plot.add_layout(
        LabelSet(
            text="labels",
            x="x",
            y="y",
            text_baseline="middle",
            text_align="left",
            source=nodes_in_equatorial_plane,
            text_color="grey",
            text_font_size="8pt",
            x_offset=10,
            y_offset=0,
        )
    )


def add_equator_line(plot):
    plot.add_layout(
        Span(
            location=0,
            dimension="width",
            line_color="green",
            line_dash="dashed",
            line_width=1,
        )
    )
    plot.add_layout(
        Label(
            text="equator",
            x=-0.9 * plots_range,
            y=0.03 * plots_range,
            text_font_size="8pt",
            text_color="green",
        )
    )


def add_equatorial_plane(plot):
    plot.add_layout(
        Label(
            text="equatorial plane",
            x=-0.7 * plots_range,
            y=0.7 * plots_range,
            text_align="center",
            text_color="green",
            text_font_size="9pt",
            angle=np.pi / 4,
        )
    )


def add_sma(plot):
    plot.segment(
        x0="a_x_start",
        x1="a_x_end",
        y0="a_y_start",
        y1="a_y_end",
        source=orbital_parameters,
        line_width=3,
        line_alpha=0.8,
        color=SMA_COLOR,
    )
    plot.add_layout(
        LabelSet(
            text="a_text",
            x="a_label_x",
            y="a_label_y",
            text_baseline="middle",
            text_align="center",
            source=orbital_parameters,
            text_color=SMA_COLOR,
            x_offset=10,
            y_offset=10,
        )
    )


def add_omega(plot):
    plot.annular_wedge(
        x=0,
        y=0,
        start_angle=0,
        end_angle="omega",
        inner_radius=8000,
        outer_radius=10000,
        color=OMEGA_COLOR,
        source=orbital_parameters,
    )
    plot.add_layout(
        LabelSet(
            text="omega_text",
            x="omega_label_x",
            y="omega_label_y",
            text_baseline="middle",
            text_align="center",
            source=orbital_parameters,
            text_color=OMEGA_COLOR,
        )
    )


def add_Gomega(plot):
    plot.annular_wedge(
        x=0,
        y=0,
        start_angle=0,
        end_angle="Gomega",
        inner_radius=8000,
        outer_radius=10000,
        color=GOMEGA_COLOR,
        source=orbital_parameters,
    )
    plot.add_layout(
        LabelSet(
            text="Gomega_text",
            x="Gomega_label_x",
            y="Gomega_label_y",
            text_baseline="middle",
            text_align="center",
            source=orbital_parameters,
            text_color=GOMEGA_COLOR,
        )
    )


def add_anomaly(plot):
    plot.annular_wedge(
        x=0,
        y=0,
        start_angle="v_start",
        end_angle="v_end",
        inner_radius=10000,
        outer_radius=12000,
        color=V_COLOR,
        source=orbital_parameters,
    )
    plot.add_layout(
        LabelSet(
            text="v_text",
            x="v_label_x",
            y="v_label_y",
            text_baseline="middle",
            text_align="center",
            source=orbital_parameters,
            text_color=V_COLOR,
        )
    )
    plot.segment(
        x0=0,
        y0=0,
        x1="x",
        y1="y",
        source=position_in_orbital_plane,
        line_width=3,
        line_alpha=0.3,
        color="grey",
    )


def generate_view(source, axis, positive):
    filter = CustomJSFilter(
        code=f"""
        var indices = [];

        for (var i = 0; i < source.get_length(); i++){{
            if (source.data['{axis}'][i] {'>' if positive else '<='} 0){{
                indices.push(true);
            }} else {{
                indices.push(false);
            }}
        }}
        return indices;
    """
    )
    return CDSView(source=source, filters=[filter])


plot_shape = create_plot(
    orbit_shape,
    "x",
    "y",
    "+z",
    position_in_orbital_plane,
    "orbit shape in orbital plane",
)
add_ascending_node_direction(plot_shape)
add_apsides_line(plot_shape)
add_sma(plot_shape)
add_omega(plot_shape)
add_anomaly(plot_shape)

plot_pole = create_plot(
    orbit_3d, "x", "y", "+z", position_3d, "orbit seen from North direction"
)
add_vernal_direction(plot_pole)
add_Gomega(plot_pole)
add_nodes_line(plot_pole)
add_equatorial_plane(plot_pole)

plot_vernal = create_plot(
    orbit_3d, "y", "z", "+x", position_3d, "orbit seen from Vernal equinox"
)
add_north_direction(plot_vernal)
add_equator_line(plot_vernal)

plot_xz = create_plot(orbit_3d, "x", "z", "-y", position_3d, "")
add_north_direction(plot_xz)
add_vernal_direction(plot_xz)
add_equator_line(plot_xz)

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
    orbit_shape=orbit_shape,
    orbit_3d=orbit_3d,
    position_in_orbital_plane=position_in_orbital_plane,
    position_3d=position_3d,
    apsides_in_orbital_plane=apsides_in_orbital_plane,
    nodes_in_equatorial_plane=nodes_in_equatorial_plane,
    sma=sma,
    eccentricity=eccentricity,
    aop=aop,
    inclination=inclination,
    raan=raan,
    anomaly=anomaly,
    N=N,
    orbit_description_div=orbit_description_div,
    orbital_parameters=orbital_parameters,
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
show(layout(style, intro, plots, footnote))
