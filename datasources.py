import numpy as np

from bokeh.models.filters import CustomJSFilter
from bokeh.models.sources import CDSView
from bokeh.models import ColumnDataSource

import constants

N = 180

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
    data=dict(
        x=constants.EARTH_RADIUS * np.cos(t),
        upper=constants.EARTH_RADIUS * np.sin(t),
        lower=-constants.EARTH_RADIUS * np.sin(t),
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
