import matplotlib.pyplot as plt
import pkg_resources


def light():
    style_path = pkg_resources.resource_filename(
        "vega_query.visualisations.styles", "theme-light.mplstyle"
    )
    plt.style.use(style_path)


def dark():
    style_path = pkg_resources.resource_filename(
        "vega_query.visualisations.styles", "theme-dark.mplstyle"
    )
    plt.style.use(style_path)
