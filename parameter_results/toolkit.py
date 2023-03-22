"""Module containing tools for visualising results from parameter tests.

Examples:
    Refer to StakeTargetScaling/nETWORKparameter_NBC_StakeTargetScaling.ipynb

Attributes:
    DEFAULT_COL_W (int):
        Default width of each column in a figure containing subplots (in inches).
    DEFAULT_ROW_H (int):
        Default height of each row in a figure containing subplots (in inches).

"""

import os
import json

import pandas as pd
import plotly.express as px
import ipywidgets as widgets

from matplotlib.axes import Axes
from IPython.display import display as dsp

from math import ceil
from typing import Optional
from itertools import product
from vega_sim.parameter_test.parameter.experiment import FILE_PATTERN, FILE_PATTERN_LOB

from matplotlib import pyplot as plt


DEFAULT_COL_W = 8
DEFAULT_ROW_H = 6


class NotebookTk:
    """Basic toolkit for common utilities needed in interactive notebooks.

    Attributes:
        widgets (dict):
            Dictionary of ipywidgets used by notebook.
    """

    def __init__(self):
        """Initialises class attributes."""
        self.widgets = dict()

    def add_widget_selectmultiple(
        self,
        key: str,
        des: str,
        options: list,
        value: Optional[list] = None,
    ):
        """Adds a new selectmultiple widget to the objects widgets dictionary.

        Args:
            key (str):
                String used as the key in the objects widget dictionary.
            des (str):
                Description displayed next to the widget in an ipynb.
            options (list):
                List of options to be displayed in the widget in an ipynb.
            value (list):
                List of default values to select in widget.

        Raises:
            ValueError():
                Raised if key already exists in objects widget dictionary.
        """

        if key in self.widgets.keys():
            raise ValueError("Specified key already exists in objects widget dict.")

        if value is None:
            value = [options[0]]

        self.widgets[key] = widgets.SelectMultiple(
            options=options, value=value, description=des, disabled=False
        )

    def add_widget_dropdown(
        self,
        key: str,
        des: str,
        options: list,
    ):
        """Adds a new dropdown widget to the objects widgets dictionary.

        Args:
            key (str):
                String used as the key in the objects widget dictionary.
            des (str):
                Description displayed next to the widget in an ipynb.
            options (list):
                List of options to be displayed in the widget in an ipynb.

        Raises:
            ValueError():
                Raised if key already exists in objects widget dictionary.
        """

        if key in self.widgets.keys():
            raise ValueError("Specified key already exists in objects widget dict.")

        self.widgets[key] = widgets.Dropdown(
            options=options,
            value=options[0],
            description=des,
            disabled=False,
        )

    def del_widget(self, key: str):
        """Deletes a widget from the objects widget dictionary.

        Args:
            key (str):
                String used as the key in the objects widget dictionary.

        Raises:
            ValueError:
                Raise if key does not exist in objects widget dictionary.
        """

        if key not in self.widgets.keys():
            raise ValueError("Specified key does not exist in objects widget dict.")

        del self.widgets[key]

    def display(
        self,
        keys: list,
    ):
        """Method displays specified widgets in an ipynb notebook.

        Args:
            keys (list):
                List of keys of widgets to include in the displayed box.
        """

        for key in keys:
            if key not in self.widgets.keys():
                raise ValueError("Specified key does not exist in objects widget dict.")

        dsp(widgets.HBox([self.widgets[key] for key in keys]))


class SingleParameterExperimentTk(NotebookTk):
    """Toolkit for analysing results from a SingleParameterExperiment.

    Class initialises an instance by first reading all data stored in the specified
    path and creating lists of pandas.DataFrame objects. Class methods can then be
    called to visualise data.

    Attributes:
        path (str):
            Path to directory containing parameter test values.
        settings(dict):
            Dictionary of parameter test settings.
        num_paravalues (int):
            Number of unique parameter values tested.
        num_iterations (int):
            Number of iterations ran.
        data_raw(list):
            List of DataFrame objects containing data for each parameter value tested.
        data_avg(list):
            List of DataFrame objects containing data averaged across iterations.
    """

    def __init__(self, path, dt, granularity) -> None:
        """Inits object by reading data stored in json and csv files in the given path.

        Method loads test settings from the 'run_config.json' and test results from csv
        files matching the FILE_PATTERN format. Test result data is converted into a
        list of pandas.DataFrame objects.

        Args:
            path (str):
                Path to directory containing parameter test files.
            dt (float):
                Float to multiply the time-step by when plotting time along the x-axis.
        """
        super().__init__()

        self.path = path

        self.dt = dt
        self.granularity = granularity

        self.settings = self._load_settings()

        self.num_paravalues = len(self.settings["tested_values"])
        self.num_iterations = self.settings["num_runs"]

        self.data_raw = self._load_data_raw()
        self.data_avg = self._load_data_avg()
        self.data_lob = self._load_data_lob()

        self._default_widgets()

    def plot_results(
        self,
        variables: Optional[list] = None,
        iterations: Optional[list] = None,
    ):
        """Plots a variables result for each iteration or averaged across iterations.

        Function visualises the results for the specified variables in the specified
        iterations. The string "avg" can be included in the iterations argument to
        plot the variables result averaged across of all iterations.

        Args:
            variables (list, optional):
                List of variables to plot. Defaults to selection in "variables" widget.
            iterations (list, optional):
                List of iterations to plot. Defaults to plotting all iterations.
        """

        if variables is None:
            variables = self.widgets["variable"].value
        if iterations is None:
            iterations = list(range(self.num_iterations))

        keys = list(product(variables, iterations))

        parameter_value_labels = [
            f"param={value}" for value in self.settings["tested_values"]
        ]
        labels = [parameter_value_labels, [""], [""]]

        cols = 2
        rows = ceil(len(keys) / 2)
        fig, axs = plt.subplots(
            rows, cols, figsize=(DEFAULT_COL_W * cols, DEFAULT_ROW_H * rows)
        )
        fig.subplots_adjust(hspace=0.4, wspace=0.4)

        for row in range(rows):
            for col in range(cols):
                if (rows == 1) and (cols == 1):
                    ax = axs
                elif (rows == 1) and (cols > 1):
                    ax = axs[col]
                elif (rows > 1) and (cols == 1):
                    ax = axs[row]
                else:
                    ax = axs[row][col]
                i = row * cols + col
                if i > len(keys) - 1:
                    fig.delaxes(ax)
                else:
                    self._add_plot(
                        ax=ax,
                        variables=[keys[i][0]],
                        iterations=[keys[i][1]],
                        ylabel=keys[i][0],
                        xlabel=f"Time [{self.granularity.name}]",
                        title=f"{keys[i][0]} // (iteration={keys[i][1]})",
                        labels=labels,
                    )

    def plot_comparison(
        self,
        parameters: Optional[list] = None,
        iterations: Optional[list] = None,
        variables: Optional[list] = None,
        formats: Optional[list] = None,
        ylabel: Optional[str] = None,
        variables_right: Optional[list] = None,
        formats_right: Optional[list] = None,
        ylabel_right: Optional[str] = None,
    ):
        """Plots a comparison of all the specified variables on the same axes.

        Creates a subplot for each combination of parameter value and iteration passed
        in as arguments and plots all the specified variables on the same axes. Plot
        appearance can be controlled through optional arguments.

        Args:
            parameters (list, optional):
                List of parameters values to plot. Defaults to all tested values.
            iterations (list, optional):
                List of iterations to plot. Defaults to all iterations.
            variables (list, optional):
                List of variables to plot on left axes. Defaults to widget selection.
            formats (list, optional):
                Nested list of formats to use on left axes. Defaults to normal lines.
            ylabel (str, optional):
                String to use as left yaxis label. Defaults to no label.
            variables_right (list, optional):
                List of variables to plot on right axes. Defaults to widget selection.
            formats_right (list, optional):
                Nested list of formats to use on right axes. Defaults to normal lines.
            ylabel_right (str, optional):
                String to use as right yaxis label. Defaults to no label.
        """

        if formats is not None:
            formats = [[""], [""], formats]
        if formats_right is not None:
            formats_right = [[""], [""], formats_right]

        if parameters is None:
            parameters = self.settings["tested_values"]
        if iterations is None:
            iterations = list(range(self.num_iterations))

        labels = [[""], [""], variables]
        labels_right = [[""], [""], variables_right]

        cols = len(iterations)
        rows = len(parameters)

        fig, axs = plt.subplots(
            rows,
            cols,
            figsize=(DEFAULT_COL_W * cols, DEFAULT_ROW_H * rows),
        )
        fig.subplots_adjust(hspace=0.4, wspace=0.4)

        for row in range(rows):
            for col in range(cols):
                if rows > 1 and cols > 1:
                    ax = axs[row, col]
                elif rows > 1:
                    ax = axs[row]
                elif cols > 1:
                    ax = axs[col]
                else:
                    ax = axs

                self._add_plot(
                    ax=ax,
                    title=f"param={parameters[row]} // iteration={iterations[col]}",
                    parameters=[parameters[row]],
                    iterations=[iterations[col]],
                    xlabel=f"Time [{self.granularity.name}]",
                    variables=variables,
                    formats=formats,
                    ylabel=ylabel,
                    variables_right=variables_right,
                    formats_right=formats_right,
                    ylabel_right=ylabel_right,
                    labels=labels,
                    labels_right=labels_right,
                )

        plt.show()

    def plot_lob(
        self,
        param_value: Optional[float] = None,
        iteration: Optional[float] = None,
    ):
        """Creates a plot of the LOB for a specified parameter value and iteration.

        Parameter value and iteration value can be passed as arguments. If no arguments
        passed, method uses values selected in widgets.

        Args:
            param_value (float, optional):
                Tested parameter value to plot results for. Defaults to widget.
            iteration:
                Iteration number to plot results for. Defaults to widget.
        """

        if param_value is None:
            param_value = self.widgets["param_value"].value
        if iteration is None:
            iteration = self.widgets["iteration"].value

        df = self._extract_lob(
            param_value=param_value,
            iteration=iteration,
        )

        fig = px.scatter_3d(
            df,
            x="Price",
            y="Time Step",
            z="Volume",
            color="Side",
            color_discrete_map={
                "Bid": "red",
                "Ask": "blue",
                "Mid": "black",
            },
            size="Volume",
        )

        fig.update_layout(
            title="3D LOB",
            autosize=False,
            width=1000,
            height=1000,
        )

        fig.show()

    def animate_lob(
        self,
        param_value: Optional[float] = None,
        iteration: Optional[float] = None,
    ):
        """Creates an animation of the LOB for a given parameter value and iteration.

        Parameter value and iteration value can be passed as arguments. If no arguments
        passed, method uses values selected in widgets.

        Args:
            param_value (float, optional):
                Tested parameter value to plot results for. Defaults to widget.
            iteration:
                Iteration number to plot results for. Defaults to widget.
        """

        if param_value is None:
            param_value = self.widgets["param_value"].value
        if iteration is None:
            iteration = self.widgets["iteration"].value

        df = self._extract_lob(
            param_value=param_value,
            iteration=iteration,
        )

        fig = px.bar(
            df,
            y="Price",
            x="Volume",
            animation_frame="Time Step",
            orientation="h",
            color="Side",
            color_discrete_map={"Bid": "red", "Ask": "blue", "Mid": "black"},
            pattern_shape="Side",
            pattern_shape_map={
                "Bid": "/",
                "Ask": "/",
                "Mid": ".",
            },
            range_x=[0, 2],
            base="Side",
        )

        fig.update_layout(
            width=800,
            height=800,
            xaxis_showgrid=True,
            yaxis_showgrid=True,
            plot_bgcolor="rgba(0,0,0,0)",
            title_text=f"LOB of Tested val {param_value, iteration}",
            showlegend=True,
        )

        fig.update_traces(width=0.001)
        fig.update_xaxes(title_text="Volume")
        fig.update_yaxes(title_text="Price")
        fig.show()

    def _load_settings(self) -> dict:
        """Loads parameter test settings stored in the 'run_config.json' in the path.

        Returns:
            dict:
                Dictionary of parameter test settings.
        """
        with open(os.path.join(self.path, "run_config.json")) as d:
            return json.load(d)

    def _load_data_raw(self) -> list:
        """Loads market data stored in '.csv' files.

        Function reads all '.csv' files where the file name matches the format defined
        in FILE_PATTERN. Files are converted to pd.DataFrame objects and stored in a
        list. The list contains one pd.DataFrame for each parameter value tested.

        Returns:
            list:
                List of pd.DataFrame objects containing market data.
        """

        data_raw = []
        for _ in range(self.num_paravalues):
            file_path = FILE_PATTERN.format(
                param_name=self.settings["parameter_tested"],
                param_value=self.settings["tested_values"][_],
            )
            data_raw.append(pd.read_csv(os.path.join(self.path, file_path)))

        return data_raw

    def _load_data_avg(self) -> list:
        """Loads average data by averaging market data across runs.

        Function groups market data in  by the time-step column and computes the mean.
        Resulting pd.DataFrame objects are stored in a new list. The list contains one
        pd.DataFrame for each parameter value tested.

        Returns:
            list:
                List of pd.DataFrame objects containing mean market data across runs.
        """

        data_avg = []
        if self.settings["num_runs"] > 1:
            for _ in range(self.num_paravalues):
                data_avg.append(
                    self.data_raw[_]
                    .groupby(self.data_raw[_]["Time Step"])
                    .mean(numeric_only=False)
                )
        else:
            for _ in range(self.num_paravalues):
                data_avg.append(
                    self.data_raw[_].set_index(self.data_raw[_]["Time Step"])
                )

        return data_avg

    def _load_data_lob(self) -> list:
        """Loads LOB data stored in '.csv' files.

        Function reads all '.csv' files where the file name matches the format defined
        in FILE_PATTERN_LOB. Files are converted to pd.DataFrame objects and stored in
        a list. The list contains one pd.DataFrame for each parameter value tested.

        Returns:
            list:
                List of pd.DataFrame objects containing LOB data.
        """

        data_lob = []
        for _ in range(self.num_paravalues):
            file_path = FILE_PATTERN_LOB.format(
                param_name=self.settings["parameter_tested"],
                param_value=self.settings["tested_values"][_],
            )
            data_lob.append(pd.read_csv(os.path.join(self.path, file_path)))

        return data_lob

    def _default_widgets(self):
        """Generates the default widgets for the class."""

        self.add_widget_dropdown(
            des="Parameter Value:",
            key="param_value",
            options=self.settings["tested_values"],
        )
        self.add_widget_dropdown(
            des="Iteration:",
            key="iteration",
            options=[i for i in range(self.num_iterations)],
        )
        self.add_widget_selectmultiple(
            des="Variable:",
            key="variable",
            options=self.data_avg[0].columns,
        )

    def _extract_lob(
        self,
        param_value: float,
        iteration: int,
    ) -> pd.DataFrame:
        """Extracts LOB data for a specific parameter value and iteration.

        Returns a pd.DataFrame which can be used in class methods to visualise LOB data
        for a specified parameter value and iteration.

        Args:
            param_index (int):
                Index of DataFrame containing desired parameter value data.
            iteration_index (int):
                Index of iteration values to match in pd.DataFrame.

        Returns:
            pd.DataFrame:
                LOB data for specified parameter value and iteration.
        """

        param_index = self.settings["tested_values"].index(param_value)

        data_raw = self.data_raw[param_index]
        data_raw = data_raw[data_raw["Iteration"] == iteration]

        data_lob = self.data_lob[param_index]
        data_lob = data_lob[data_lob["Iteration"] == iteration]

        new_data_list = []

        for i in range(data_lob.shape[0]):
            res_bid = data_lob["Order Book Bid Side"].iloc[i]
            res_ask = data_lob["Order Book Ask Side"].iloc[i]
            time_step = data_lob["Time Step"].iloc[i]
            res_bid = res_bid[1:-1]
            res_bid = res_bid.split(", ")
            res_ask = res_ask[1:-1]
            res_ask = res_ask.split(", ")
            for _ in range(len(res_bid)):
                tmp = res_bid[_].split(": ")
                if len(tmp) == 2:
                    result = {}
                    result["Time Step"] = time_step
                    result["Price"] = float(tmp[0])
                    result["Volume"] = float(tmp[1])
                    result["Side"] = "Bid"
                    new_data_list.append(result)

            for _ in range(len(res_ask)):
                tmp = res_ask[_].split(": ")
                if len(tmp) == 2:
                    result = {}
                    result["Time Step"] = time_step
                    result["Price"] = float(tmp[0])
                    result["Volume"] = float(tmp[1])
                    result["Side"] = "Ask"
                    new_data_list.append(result)

            result = {}
            result["Time Step"] = time_step
            result["Price"] = data_raw.loc[
                time_step + iteration * (data_raw.shape[0]) - 1,
                "External Midprice",
            ]
            result["Side"] = "Mid"
            result["Volume"] = 0.05
            new_data_list.append(result)

        return pd.DataFrame(new_data_list)

    def _add_plot(
        self,
        ax: Axes,
        variables: list,
        variables_right: Optional[list] = None,
        parameters: Optional[list] = None,
        iterations: list = ["avg"],
        formats: Optional[list] = None,
        formats_right: Optional[list] = None,
        ylabel: Optional[str] = None,
        ylabel_right: Optional[str] = None,
        xlabel: Optional[str] = None,
        title: Optional[str] = None,
        labels: Optional[list] = None,
        labels_right: Optional[list] = None,
    ):
        """Adds a complete plot to a given subplot axes.

        Args:
            ax (Axes):
                Handles to matplotlib Axes object in which to plot data.
            variables (list):
                List of variables to plot in left axes.
            variables_right (list, optional):
                List of variables to plot on right axes. Defaults to None.
            parameters (list, optional):
                List of parameters to plot on left and right axes. Defaults to all values.
            iterations (list, optional):
                List of iterations to plot on left and right axes. Defaults to ["avg"].
            formats (list, optional):
                Nested list of formats to use on left axes. Defaults to normal lines.
            formats_right (list, optional):
                Nested list of formats to use on left axes. Defaults to normal lines.
            ylabel (str, optional):
                String to use as left yaxis label. Defaults to no label.
            ylabel_right (str, optional):
                String to use as right yaxis label. Defaults to no label.
            xlabel (str, optional):
                String to use as xaxis label: Defaults to no label.
            title (str, optional):
                String to use as axis title. Defaults to no title.
            labels (list, optional):
                Nested list of labels to use. Defaults to full information.
            labels_right (list, optional):
                Nested list of labels to use. Defaults to full information.

        """

        if parameters is None:
            parameters = self.settings["tested_values"]

        lns = self._add_data(
            ax=ax,
            variables=variables,
            formats=formats,
            parameters=parameters,
            iterations=iterations,
            labels=labels,
        )

        if variables_right is not None:
            ax_right = ax.twinx()
            lns_right = self._add_data(
                ax=ax_right,
                variables=variables_right,
                formats=formats_right,
                parameters=parameters,
                iterations=iterations,
                labels=labels_right,
            )
            lns = lns + lns_right

        if labels is not None:
            lns = [item for sublist in lns for item in sublist]
            labels = [ln.get_label() for ln in lns]
            ax.legend(lns, labels, loc=0)

        if ylabel is not None:
            ax.set_ylabel(ylabel)
        if ylabel_right is not None:
            ax_right.set_ylabel(ylabel_right)
        if title is not None:
            ax.set_title(title)
        if xlabel is not None:
            ax.set_xlabel(xlabel)

    def _add_data(
        self,
        ax: Axes,
        variables: list,
        formats: Optional[list] = None,
        parameters: Optional[list] = None,
        iterations: list = ["avg"],
        labels: Optional[list] = None,
    ):
        """Adds a plot to a specific axes of a subplot.

        Args:
            ax (Axes):
                Handles to matplotlib Axes object in which to plot data.
            variables (list):
                List of variables to plot in axis.
            parameters (list, optional):
                List of parameters to plot on axes. Defaults to all values.
            iterations (list, optional):
                List of iterations to plot on axes. Defaults to ["avg"].
            formats (list, optional):
                Nested list of formats to use. Defaults to normal lines.
            ylabel (str, optional):
                String to use as  axis label. Defaults to no label.
            labels (list, optional):
                Nested list of labels to use. Defaults to full information.

        Returns:
            list:
                A list of matplotlib Line objects.
        """

        lns = []

        if parameters is None:
            parameters = self.settings["tested_values"]

        for i, parameter in enumerate(parameters):
            parameter_index = self.settings["tested_values"].index(parameter)

            for j, iteration in enumerate(iterations):
                if iteration == "avg":
                    df = self.data_avg[parameter_index]

                    for k, variable in enumerate(variables):
                        if formats is None:
                            fmt = "-"
                        else:
                            fmt = formats[0][i] + formats[1][j] + formats[2][k]
                        xdata = df.index * self.dt / self.granularity.value
                        ydata = df[variable]
                        label = f"{labels[0][i]}  {labels[1][j]}  {labels[2][k]}"
                        lns.append(ax.plot(xdata, ydata, fmt, label=label))

                else:
                    df = self.data_raw[parameter_index][
                        self.data_raw[parameter_index]["Iteration"] == iteration
                    ]

                    for k, variable in enumerate(variables):
                        if formats is None:
                            fmt = "-"
                        else:
                            fmt = formats[0][i] + formats[1][j] + formats[2][k]
                        xdata = df.index * self.dt / self.granularity.value
                        ydata = df[variable]
                        label = f"{labels[0][i]}  {labels[1][j]}  {labels[2][k]}"
                        lns.append(ax.plot(xdata, ydata, fmt, label=label))

        if "Market State" in variables:
            self._market_state_ticks(ax)

        return lns

    @staticmethod
    def _market_state_ticks(ax):
        """Modifies axes ticks with human readable market states.

        Args:
            ax (Axes):
                Handles to axis to modify.
        """
        ax.set_yticks([4, 5, 6, 7, 8, 9])
        ax.set_yticklabels(
            ["", "Active", "Suspended", "", "", "Settled"], rotation=-90, va="center"
        )
