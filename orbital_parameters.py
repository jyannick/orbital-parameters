
''' Rewrite the basic sliders example as a standalone document with JavaScript callbacks.
Present an interactive function explorer with slider widgets.
Scrub the sliders to change the properties of the ``sin`` curve, or
type into the title text box to update the title of the plot.
Run example with python sliders-standalone-code.py
In this version, the callbacks are written as strings of JS code.
'''
import numpy as np

from bokeh.layouts import grid, widgetbox
from bokeh.models import ColumnDataSource, Band
from bokeh.models.callbacks import CustomJS
from bokeh.models.widgets import Slider, TextInput, Button
from bokeh.plotting import figure, output_notebook, output_file, show
from bokeh.models.annotations import Arrow, Label, Span
from bokeh.models.arrow_heads import VeeHead

output_file("orbital-parameters.html")
# Set up data
N = 180
Re = 6378 # km
max_sma = 50000 #km
plots_range = 80000 #km, half range
x = np.zeros(N)
y = np.zeros(N)
z = np.zeros(N)
orbit_shape = ColumnDataSource(data=dict(x=x, y=y))
position_in_orbital_plane = ColumnDataSource(data=dict(x=np.zeros(1), y=np.zeros(1)))
orbit_3d = ColumnDataSource(data=dict(x=x, y=y, z=z))
position_3d = ColumnDataSource(data=dict(x=np.zeros(1), y=np.zeros(1), z=np.zeros(1)))

t = np.linspace(0, np.pi, 10)
earth = ColumnDataSource(data=dict(x=Re*np.cos(t), upper=Re*np.sin(t), lower=-Re*np.sin(t)))

# Set up plots
def create_plot(source, x, y, sat_position, title):
    plot = figure(plot_height=400, plot_width=400, title=title,
                x_range=[-plots_range, plots_range], y_range=[-plots_range, plots_range], toolbar_location=None)

    plot.line(x, y, source=source, line_width=3, line_alpha=0.6)
    plot.circle_cross(x, y, source=sat_position, color='red', size=10, fill_alpha=0.2)
    plot.add_layout(Band(base='x', lower='lower', upper='upper', source=earth, 
                level='underlay', fill_alpha=0.5, line_width=1, line_color='grey', fill_color='grey'))
    return plot

def add_north_direction(plot):
    plot.add_layout(Arrow(end=VeeHead(size=10), line_width=3,
                   x_start=0, y_start=0.5*plots_range, x_end=0, y_end=plots_range))
    plot.add_layout(Label(text="North", x=0.05*plots_range, y=0.8*plots_range, text_font_size='8pt'))

def add_vernal_direction(plot):
    plot.add_layout(Arrow(end=VeeHead(size=10), line_width=3,
                   x_start=0.5*plots_range, y_start=0, x_end=plots_range, y_end=0))
    plot.add_layout(Label(text="Vernal equinox", x=0.5*plots_range, y=-0.1*plots_range, text_font_size='8pt'))

def add_ascending_node_direction(plot):
    plot.add_layout(Arrow(end=VeeHead(size=10), line_width=3,
                   x_start=0, y_start=0, x_end=0.3*plots_range, y_end=0))
    plot.add_layout(Label(text="ascending node", x=0.33*plots_range, y=-0.03*plots_range, text_font_size='8pt'))

def add_equator_line(plot):
    plot.add_layout(Span(location=0,
                         dimension='width', line_color='green',
                         line_dash='dashed', line_width=1))
    plot.add_layout(Label(text='equator', x=-0.9*plots_range, y=0.03*plots_range, text_font_size='8pt', text_color='green'))

plot_shape = create_plot(orbit_shape, 'x', 'y', position_in_orbital_plane, 'orbit shape in orbital plane')
add_ascending_node_direction(plot_shape)

plot_pole = create_plot(orbit_3d, 'x', 'y', position_3d, 'orbit seen from North direction')
add_vernal_direction(plot_pole)

plot_vernal = create_plot(orbit_3d, 'y', 'z', position_3d, 'orbit seen from Vernal equinox')
add_north_direction(plot_vernal)
add_equator_line(plot_vernal)

plot_xz = create_plot(orbit_3d, 'x', 'z', position_3d, '')
add_north_direction(plot_xz)
add_vernal_direction(plot_xz)
add_equator_line(plot_xz)


# Set up widgets
sma = Slider(title="semi-major axis (km)", value=42164, start=0, end=max_sma, step=10)
eccentricity = Slider(title="eccentricity (-)", value=0.7, start=0, end=1, step=0.01)
aop = Slider(title="argument of perigee (deg)", value=0, start=0, end=360, step=1)
inclination = Slider(title="inclination (deg)", value=0, start=0, end=180, step=1)
raan = Slider(title="right ascension of ascending node (deg)", value=0, start=0, end=360, step=1)
anomaly = Slider(title="true anomaly (deg)", value=0, start=0, end=360, step=2)

# Set up callbacks
sliders_callback_code=f"""
    const a = sma.value,
        e = eccentricity.value,
        N = {N},
        b = a * window.Math.sqrt(1 - e**2),
        c = window.Math.sqrt(a**2 - b**2),
        omega = aop.value * window.Math.PI / 180,
        inc = inclination.value * window.Math.PI / 180,
        Gomega = raan.value * window.Math.PI / 180,
        anomaly_index = window.Math.round(anomaly.value / 360 * (N+1)),
        x_shape = orbit_shape.data['x'],
        y_shape = orbit_shape.data['y'],
        x_sat_in_orbital_plane = position_in_orbital_plane.data['x'],
        y_sat_in_orbital_plane = position_in_orbital_plane.data['y'],
        x_sat = position_3d.data['x'],
        y_sat = position_3d.data['y'],
        z_sat = position_3d.data['z'],
        x=orbit_3d.data['x'],
        y=orbit_3d.data['y'],
        z=orbit_3d.data['z']

    for(let i=0; i < N; i++) {{
        let t = i/(N-1) * 2 * window.Math.PI
        let cos_omega = window.Math.cos(omega)
        let sin_omega = window.Math.sin(omega)
        let cos_t = window.Math.cos(t)
        let sin_t = window.Math.sin(t)
        let cos_i = window.Math.cos(inc)
        let sin_i = window.Math.sin(inc)
        let cos_Gomega = window.Math.cos(Gomega)
        let sin_Gomega = window.Math.sin(Gomega)

        x_shape[i] = a * cos_omega * cos_t - b * sin_omega * sin_t - c * cos_omega
        y_shape[i] = a * sin_omega * cos_t + b * cos_omega * sin_t - c * sin_omega
        
        let x_incli_only = - x_shape[i]
        let y_incli_only = - y_shape[i] * cos_i
        let z_incli_only =   y_shape[i] * sin_i

        x[i] = x_incli_only * cos_Gomega - y_incli_only * sin_Gomega
        y[i] = x_incli_only * sin_Gomega + y_incli_only * cos_Gomega
        z[i] = z_incli_only
    }}

    x_sat_in_orbital_plane[0] = x_shape[anomaly_index]
    y_sat_in_orbital_plane[0] = y_shape[anomaly_index]
    x_sat[0] = x[anomaly_index]
    y_sat[0] = y[anomaly_index]
    z_sat[0] = z[anomaly_index]

    orbit_shape.change.emit()
    orbit_3d.change.emit()
    position_in_orbital_plane.change.emit()
    position_3d.change.emit()
"""

slider_args = dict(orbit_shape=orbit_shape, orbit_3d=orbit_3d, position_in_orbital_plane=position_in_orbital_plane, position_3d=position_3d,
sma=sma, eccentricity=eccentricity, aop=aop, inclination=inclination, raan=raan, anomaly=anomaly)

for w in [sma, eccentricity, aop, inclination, raan, anomaly]:
    w.js_on_change('value', CustomJS(args=slider_args, code=sliders_callback_code))

# Set up layouts and add to document
inputs = widgetbox(sma, eccentricity, aop, inclination, raan, anomaly)

show(grid([[inputs, plot_vernal, plot_xz], [plot_shape, None, plot_pole]]))