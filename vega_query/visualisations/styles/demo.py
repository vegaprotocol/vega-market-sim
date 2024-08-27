import argparse

import matplotlib.pyplot as plt
import vega_query.visualisations as vis


import matplotlib.axes as axes
import matplotlib.figure as figure


def _step_demo(ax: axes.Axes):
    ax.set_title("title")
    ax.set_xlabel("xlabel")
    ax.set_ylabel("ylabel")
    for i in range(len(plt.rcParams["axes.prop_cycle"])):
        x = [i for i in range(10)]
        y = [x * i for x in x]
        ax.plot(x, y)


def _bar_demo(ax: axes.Axes):
    ax.set_title("title")
    ax.set_xlabel("xlabel")
    ax.set_ylabel("ylabel")
    for i in range(len(plt.rcParams["axes.prop_cycle"])):
        ax.bar(i, i + 1)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--style", type=str, default="dark")
    args = parser.parse_args()

    match args.style:
        case "dark":
            vis.styles.dark()
        case "light":
            vis.styles.light()
        case _:
            raise ValueError(f"Invalid style: {args.style}")

    _step_demo(plt.figure().add_subplot())
    _bar_demo(plt.figure().add_subplot())

    plt.show()
