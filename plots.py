from numpy import pi

from bokeh.models import LabelSet, Band
from bokeh.models.annotations import Arrow, Label, Span
from bokeh.models.arrow_heads import VeeHead
from bokeh.plotting import figure

import constants
from colors import colors
from datasources import earth, generate_view


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
        x_range=[-constants.PLOTS_RANGE, constants.PLOTS_RANGE],
        y_range=[-constants.PLOTS_RANGE, constants.PLOTS_RANGE],
        background_fill_color=colors["background"],
        border_fill_color=colors["elements-background"],
        outline_line_alpha=0,
    )
    plot.title.text_color = colors["text-dimmed"]
    plot.grid.visible = False
    plot.axis.visible = False
    plot.line(
        x,
        y,
        source=source,
        line_width=3,
        line_dash="dashed",
        line_color=colors["orbit"],
    )
    plot.circle(
        x,
        y,
        source=source,
        view=generate_view(source, depth_coordinate, depth_is_positive),
        size=5,
        color=colors["orbit"],
    )
    plot.circle(
        x,
        y,
        source=sat_position,
        color=colors["satellite"],
        size=10,
    )
    plot.add_layout(
        Band(
            base="x",
            lower="lower",
            upper="upper",
            source=earth,
            level="underlay",
            fill_alpha=0.5,
            line_width=1,
            line_color=colors["earth"],
            fill_color=colors["earth"],
        )
    )
    return plot


def add_north_direction(plot):
    plot.add_layout(
        Arrow(
            end=VeeHead(
                size=10, fill_color=colors["north"], line_color=colors["north"]
            ),
            line_width=3,
            x_start=0,
            y_start=0,
            x_end=0,
            y_end=constants.PLOTS_RANGE,
            line_color=colors["north"],
        )
    )
    plot.add_layout(
        Label(
            text="North",
            x=0.05 * constants.PLOTS_RANGE,
            y=0.8 * constants.PLOTS_RANGE,
            text_font_size="8pt",
            text_color=colors["north"],
        )
    )


def add_vernal_direction(plot):
    plot.add_layout(
        Arrow(
            end=VeeHead(
                size=10, fill_color=colors["vernal"], line_color=colors["vernal"]
            ),
            line_width=3,
            x_start=0,
            y_start=0,
            x_end=constants.PLOTS_RANGE,
            y_end=0,
            line_color=colors["vernal"],
        )
    )
    plot.add_layout(
        Label(
            text="Vernal Equinox",
            x=0.5 * constants.PLOTS_RANGE,
            y=-0.1 * constants.PLOTS_RANGE,
            text_font_size="8pt",
            text_color=colors["vernal"],
        )
    )


def add_ascending_node_direction(plot):
    plot.add_layout(
        Arrow(
            end=VeeHead(
                size=10,
                fill_color=colors["ascending-node"],
                line_color=colors["ascending-node"],
            ),
            line_width=3,
            x_start=0,
            y_start=0,
            x_end=constants.PLOTS_RANGE,
            y_end=0,
            line_color=colors["ascending-node"],
        )
    )
    plot.add_layout(
        Label(
            text="Ascending Node",
            x=0.5 * constants.PLOTS_RANGE,
            y=-0.1 * constants.PLOTS_RANGE,
            text_font_size="8pt",
            text_color=colors["ascending-node"],
        )
    )


def add_apsides_line(plot, apsides_in_orbital_plane):
    plot.line(
        "x",
        "y",
        source=apsides_in_orbital_plane,
        line_width=3,
        line_alpha=0.3,
        color=colors["apsides"],
    )


def add_nodes_line(plot, nodes_in_equatorial_plane):
    plot.line(
        "x",
        "y",
        source=nodes_in_equatorial_plane,
        line_width=3,
        line_alpha=0.3,
        color=colors["nodes"],
    )
    plot.add_layout(
        LabelSet(
            text="labels",
            x="x",
            y="y",
            text_baseline="middle",
            text_align="left",
            source=nodes_in_equatorial_plane,
            text_color=colors["nodes"],
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
            line_color=colors["equator"],
            line_dash="dashed",
            line_width=1,
        )
    )
    plot.add_layout(
        Label(
            text="Equator",
            x=-0.9 * constants.PLOTS_RANGE,
            y=0.03 * constants.PLOTS_RANGE,
            text_font_size="8pt",
            text_color=colors["equator"],
        )
    )


def add_equatorial_plane(plot):
    plot.add_layout(
        Label(
            text="Equatorial Plane",
            x=-0.7 * constants.PLOTS_RANGE,
            y=0.7 * constants.PLOTS_RANGE,
            text_align="center",
            text_color=colors["equator"],
            text_font_size="9pt",
            angle=pi / 4,
        )
    )


def add_sma(plot, orbital_parameters):
    plot.segment(
        x0="a_x_start",
        x1="a_x_end",
        y0="a_y_start",
        y1="a_y_end",
        source=orbital_parameters,
        line_width=3,
        line_alpha=0.8,
        color=colors["sma"],
    )
    plot.add_layout(
        LabelSet(
            text="a_text",
            x="a_label_x",
            y="a_label_y",
            text_baseline="middle",
            text_align="center",
            source=orbital_parameters,
            text_color=colors["sma"],
            x_offset=10,
            y_offset=10,
        )
    )


def add_eccentricity(plot, orbital_parameters):
    plot.segment(
        x0="a_x_start",
        x1=0,
        y0="a_y_start",
        y1=0,
        source=orbital_parameters,
        line_width=3,
        line_alpha=0.8,
        color=colors["eccentricity"],
    )
    plot.add_layout(
        LabelSet(
            text="e_text",
            x="e_label_x",
            y="e_label_y",
            text_baseline="middle",
            text_align="center",
            source=orbital_parameters,
            text_color=colors["eccentricity"],
            x_offset=10,
            y_offset=10,
        )
    )


def add_omega(plot, orbital_parameters):
    plot.annular_wedge(
        x=0,
        y=0,
        start_angle=0,
        end_angle="omega",
        inner_radius=8000,
        outer_radius=10000,
        color=colors["omega"],
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
            text_color=colors["omega"],
        )
    )


def add_Gomega(plot, orbital_parameters):
    plot.annular_wedge(
        x=0,
        y=0,
        start_angle=0,
        end_angle="Gomega",
        inner_radius=8000,
        outer_radius=10000,
        color=colors["Gomega"],
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
            text_color=colors["Gomega"],
        )
    )


def add_anomaly(plot, orbital_parameters, position_in_orbital_plane):
    plot.annular_wedge(
        x=0,
        y=0,
        start_angle="v_start",
        end_angle="v_end",
        inner_radius=10000,
        outer_radius=12000,
        color=colors["anomaly"],
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
            text_color=colors["anomaly"],
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
        color=colors["anomaly"],
    )
