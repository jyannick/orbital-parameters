import numpy as np

from bokeh.layouts import column, gridplot, layout
from bokeh.models import ColumnDataSource, Band, Div
from bokeh.models.callbacks import CustomJS
from bokeh.models.widgets import Slider
from bokeh.plotting import figure, output_file, show
from bokeh.models.annotations import Arrow, Label, Span
from bokeh.models.arrow_heads import VeeHead
from bokeh.models.filters import CustomJSFilter
from bokeh.models.sources import CDSView

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

orbit_3d = ColumnDataSource(data=dict(x=x, y=y, z=z))
position_3d = ColumnDataSource(data=dict(x=np.zeros(1), y=np.zeros(1), z=np.zeros(1)))

t = np.linspace(0, np.pi, 10)
earth = ColumnDataSource(
    data=dict(x=Re * np.cos(t), upper=Re * np.sin(t), lower=-Re * np.sin(t))
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
    )
    plot.line(x, y, source=source, line_width=3, line_alpha=0.6)
    plot.line(
        x,
        y,
        source=source,
        view=generate_view(source, depth_coordinate, depth_is_positive),
        line_width=5,
        alpha=0.5,
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
            end=VeeHead(size=10),
            line_width=3,
            x_start=0,
            y_start=0.5 * plots_range,
            x_end=0,
            y_end=plots_range,
        )
    )
    plot.add_layout(
        Label(
            text="North",
            x=0.05 * plots_range,
            y=0.8 * plots_range,
            text_font_size="8pt",
        )
    )


def add_vernal_direction(plot):
    plot.add_layout(
        Arrow(
            end=VeeHead(size=10),
            line_width=3,
            x_start=0.5 * plots_range,
            y_start=0,
            x_end=plots_range,
            y_end=0,
        )
    )
    plot.add_layout(
        Label(
            text="Vernal equinox",
            x=0.5 * plots_range,
            y=-0.1 * plots_range,
            text_font_size="8pt",
        )
    )


def add_ascending_node_direction(plot):
    plot.add_layout(
        Arrow(
            end=VeeHead(size=10),
            line_width=3,
            x_start=0,
            y_start=0,
            x_end=0.3 * plots_range,
            y_end=0,
        )
    )
    plot.add_layout(
        Label(
            text="ascending node",
            x=0.33 * plots_range,
            y=-0.03 * plots_range,
            text_font_size="8pt",
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

plot_pole = create_plot(
    orbit_3d, "x", "y", "+z", position_3d, "orbit seen from North direction"
)
add_vernal_direction(plot_pole)

plot_vernal = create_plot(
    orbit_3d, "y", "z", "+x", position_3d, "orbit seen from Vernal equinox"
)
add_north_direction(plot_vernal)
add_equator_line(plot_vernal)

plot_xz = create_plot(orbit_3d, "x", "z", "-y", position_3d, "")
add_north_direction(plot_xz)
add_vernal_direction(plot_xz)
add_equator_line(plot_xz)


# Set up widgets
sma = Slider(title="semi-major axis (km)", value=42164, start=0, end=max_sma, step=10)
eccentricity = Slider(title="eccentricity (-)", value=0.7, start=0, end=1, step=0.01)
aop = Slider(title="argument of perigee (deg)", value=0, start=0, end=360, step=1)
inclination = Slider(title="inclination (deg)", value=0, start=0, end=180, step=1)
raan = Slider(
    title="right ascension of ascending node (deg)", value=0, start=0, end=360, step=1
)
anomaly = Slider(title="true anomaly (deg)", value=0, start=0, end=359, step=1)

# Set up callbacks
sliders_callback_code = """
    const a = sma.value,
        e = eccentricity.value,
        p = a * (1 - e*e),
        omega = aop.value * window.Math.PI / 180,
        inc = inclination.value * window.Math.PI / 180,
        Gomega = raan.value * window.Math.PI / 180,
        mu = 3.986004418e14,
        earth_radius = 6378,
        anomaly_index = window.Math.round(anomaly.value / 360 * N),
        x_shape = orbit_shape.data['x'],
        y_shape = orbit_shape.data['y'],
        x_sat_in_orbital_plane = position_in_orbital_plane.data['x'],
        y_sat_in_orbital_plane = position_in_orbital_plane.data['y'],
        x_sat = position_3d.data['x'],
        y_sat = position_3d.data['y'],
        z_sat = position_3d.data['z'],
        x = orbit_3d.data['x'],
        y = orbit_3d.data['y'],
        z = orbit_3d.data['z'],
        x_apsides_in_orbital_plane = apsides_in_orbital_plane.data['x'],
        y_apsides_in_orbital_plane = apsides_in_orbital_plane.data['y']

    let cos_omega = window.Math.cos(omega)
    let sin_omega = window.Math.sin(omega)
    let cos_Gomega = window.Math.cos(Gomega)
    let sin_Gomega = window.Math.sin(Gomega)
    let cos_i = window.Math.cos(inc)
    let sin_i = window.Math.sin(inc)

    for(let i=0; i < N; i++) {
        let v = i/(N-1) * 2 * window.Math.PI
        let cos_v = window.Math.cos(v)
        let sin_v = window.Math.sin(v)
        let r = p / (1 + e * cos_v)

        x_shape[i] = r * cos_omega * cos_v - r * sin_omega * sin_v
        y_shape[i] = r * sin_omega * cos_v + r * cos_omega * sin_v

        let x_incli_only = - x_shape[i]
        let y_incli_only = - y_shape[i] * cos_i
        let z_incli_only =   y_shape[i] * sin_i

        x[i] = x_incli_only * cos_Gomega - y_incli_only * sin_Gomega
        y[i] = x_incli_only * sin_Gomega + y_incli_only * cos_Gomega
        z[i] = z_incli_only
    }

    x_apsides_in_orbital_plane[0] = a*(1-e)*cos_omega
    y_apsides_in_orbital_plane[0] = a*(1-e)*sin_omega
    x_apsides_in_orbital_plane[1] = -a*(1+e)*cos_omega
    y_apsides_in_orbital_plane[1] = -a*(1+e)*sin_omega

    x_sat_in_orbital_plane[0] = x_shape[anomaly_index]
    y_sat_in_orbital_plane[0] = y_shape[anomaly_index]
    x_sat[0] = x[anomaly_index]
    y_sat[0] = y[anomaly_index]
    z_sat[0] = z[anomaly_index]

    orbit_shape.change.emit()
    orbit_3d.change.emit()
    position_in_orbital_plane.change.emit()
    position_3d.change.emit()
    apsides_in_orbital_plane.change.emit()

    let orbital_period_hours = 2*window.Math.PI * window.Math.sqrt((a*1000)**3/mu)/3600
    let apogee_altitude = a*(1+e)-earth_radius
    let perigee_altitude = a*(1-e)-earth_radius

    orbit_description_div.text = `
        <h2>Orbital Data</h2>
        <ul>
            <li>Orbital period: ${orbital_period_hours.toFixed(3)} hours</li>
            <li>Apogee altitude: ${apogee_altitude.toFixed(0)} kilometers</li>
            <li>Perigee altitude: ${perigee_altitude.toFixed(0)} kilometers</li>
        </ul>`
"""

orbit_description_div = Div(
    text="""
<h2>Orbital Data</h2>
<p>Please manipulate the sliders to update this data.</p>
"""
)


callback_args = dict(
    orbit_shape=orbit_shape,
    orbit_3d=orbit_3d,
    position_in_orbital_plane=position_in_orbital_plane,
    position_3d=position_3d,
    apsides_in_orbital_plane=apsides_in_orbital_plane,
    sma=sma,
    eccentricity=eccentricity,
    aop=aop,
    inclination=inclination,
    raan=raan,
    anomaly=anomaly,
    N=N,
    orbit_description_div=orbit_description_div,
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
show(layout(intro, plots))
