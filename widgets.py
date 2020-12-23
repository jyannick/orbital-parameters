from bokeh.models.widgets import Slider, Spinner
from bokeh.layouts import row


def build_orbital_parameter(title, css_class, start, end, step, value):
    slider = Slider(
        title=title,
        value=value,
        start=start,
        end=end,
        step=step,
        css_classes=["slider", f"{css_class}_slider"],
    )

    spinner = Spinner(
        low=start,
        high=end,
        value=value,
        step=step,
        width=80,
        css_classes=["spinner", f"{css_class}_spinner"],
    )
    spinner.js_link("value", slider, "value")
    slider.js_link("value", spinner, "value")
    layout = row(slider, spinner, css_classes=[f"{css_class}_layout"])
    return (layout, slider)
