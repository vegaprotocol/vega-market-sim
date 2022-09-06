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
from sqlite3 import paramstyle
import pandas as pd
import matplotlib.pyplot as plt
from math import ceil
from matplotlib.axes import Axes
from matplotlib import pyplot as plt
import plotly.express as px
import ipywidgets as widgets
from IPython.display import display
from vega_sim.parameter_test.parameter.experiment import FILE_PATTERN, FILE_PATTERN_LOB

DEFAULT_COL_W = 8
DEFAULT_ROW_H = 6


class SingleParameterTest:
    """Class for loading and visualising data from a single parameter test.

    Class initialises an instance by first reading all data stored in the specified
    path and creating lists of pandas.DataFrame objects. Class methods can then be
    called to visualise data.

    Attributes:
        path (str):
            Path to directory containing parameter test values.
        setting(dict):
            Dictionary of parameter test settings.
        num_paravalues (int):
            Number of unique parameter values tested.
        num_iterations (int):
            Number of iterations ran.
        data(list):
            List of DataFrame objects containing data for each parameter value tested.
        data_avg(list):
            List of DataFrame objects containing data averaged across iterations.
    """

    def __init__(self, path) -> None:
        """Inits object by reading data stored in json and csv files in the given path.

        Method loads test settings from the 'run_config.json' and test results from csv
        files matching the FILE_PATTERN format. Test result data is converted into a
        list of pandas.DataFrame objects.

        Args:
            path (str): Path to directory containing parameter test files.
        """

        self.path = path

        self.setting = self._load_settings()

        self.num_paravalues = len(self.setting["tested_values"])
        self.num_iterations = self.setting["num_runs"]

        self.data_raw = self._load_data_raw()
        self.data_avg = self._load_data_avg()
        self.data_lob = self._load_data_lob()

        self.widgets = dict()

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
                param_name=self.setting["parameter_tested"],
                param_value=self.setting["tested_values"][_],
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
        if self.setting["num_runs"] > 1:
            for _ in range(self.num_paravalues):
                data_avg.append(
                    self.data_raw[_].groupby(self.data_raw[_]["Time Step"]).mean()
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
                param_name=self.setting["parameter_tested"],
                param_value=self.setting["tested_values"][_],
            )
            data_lob.append(pd.read_csv(os.path.join(self.path, file_path)))

        return data_lob

    def _extract_lob(self, param_index: int, iteration_index: int) -> pd.DataFrame:
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

        data_raw = self.data_raw[param_index]
        data_raw = data_raw[data_raw["Iteration"] == iteration_index]

        data_lob = self.data_lob[param_index]
        data_lob = data_lob[data_lob["Iteration"] == iteration_index]

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
            if time_step != 289:
                result = {}
                result["Time Step"] = time_step
                result["Price"] = data_raw.loc[
                    time_step - 1 + iteration_index * (data_raw.shape[0] - 1),
                    "External Midprice",
                ]
                result["Side"] = "Mid"
                result["Volume"] = 0.05
                new_data_list.append(result)

        return pd.DataFrame(new_data_list)

    def vis_metrics_over_time(self, dt: float, metrics: list = None):
        """Utility for visualising market metrics over time.

        Args:
            metrics (list, optional):
                List of metric strings to plot.
            dt (float, optional):
                Value to scale all time-step values by.
        """
        if metrics is None:
            metrics = list(self.data_avg[0].columns)

        cols = 2
        rows = ceil(len(metrics) / cols)

        labels = [
            f"{self.setting['parameter_tested']}={self.setting['tested_values'][i]}"
            for i in range(self.num_paravalues)
        ]

        fig = plt.figure(figsize=(cols * 8, rows * 6))

        for row in range(rows):
            for col in range(cols):

                i = row * cols + col

                if i > len(metrics) - 1:
                    break

                metric = metrics[i]

                xdata = []
                ydata = []
                for j in range(self.num_paravalues):
                    xdata.append(self.data_avg[j].index * dt)
                    ydata.append(self.data_avg[j][metric])

                ax = fig.add_subplot(rows, cols, i + 1)

                self.line_plot(
                    ax=ax,
                    xdata=xdata,
                    ydata=ydata,
                    labels=labels,
                    title=f"{metrics[i]} over time",
                    xlabel="Time (hours)",
                    ylabel=metric,
                    loc="lower right",
                )

                plt.subplots_adjust(hspace=0.5, wspace=0.3)

        plt.show()

    def vis_mid_mark_state(self, dt: float):
        """Utility for visualising mid-price, mark-price, and market-state over time.

        Each figure row contains subplots for a tested marked parameter. Each figure
        column contains subplots for a specific market iteration.

        Args:
            dt (float): Value to scale all time-step values by.
        """

        cols = max(self.data_raw[0]["Iteration"]) + 1
        rows = len(self.setting["tested_values"])

        fig = plt.figure(figsize=(cols * 8, rows * 6))

        for row in range(rows):
            for col, iter_df in self.data_raw[row].groupby("Iteration"):

                i = row * cols + col

                left_ax = fig.add_subplot(rows, cols, i + 1)
                self.line_plot(
                    ax=left_ax,
                    xdata=[self.data_avg[row].index * dt] * 2,
                    ydata=[iter_df["External Midprice"], iter_df["Markprice"]],
                    formats=["--", "-"],
                    labels=[f"Iter {col} External Mid", f"Iter {col} Mark"],
                    title=f"Tested Value={self.setting['tested_values'][row]} // Iteration={col}",
                    xlabel="Time (hours)",
                    ylabel="Price",
                    loc="upper left",
                )
                right_ax = left_ax.twinx()
                self.line_plot(
                    ax=right_ax,
                    xdata=[self.data_avg[row].index * dt],
                    ydata=[iter_df["Market State"]],
                    formats=["r."],
                    labels=[f"Iter {col} State"],
                    xlabel="Time (hours)",
                    ylabel="Market State",
                    loc="lower right",
                )
                right_ax.set_yticks(range(4, 10))
                right_ax.set_yticklabels(
                    labels=["", "Active", "Suspended", "", "", "Settled"],
                    rotation=-90,
                    va="center",
                    fontsize=8,
                )

                plt.subplots_adjust(hspace=0.4, wspace=0.4)

        plt.show()

    def value_iteration_dropdown(self):
        """Creates a widget to select a tested parameter value and iteration number.

        Utility creates a box with two dropdown widgets. The first dropdown allows user
        to select a tested parameter value from the list of tested values. The second
        dropdown allows the user to select an iteration number up to the number of
        iterations ran in the parameter test.

        """
        values = [
            int(i) if i.isdigit() else float(i) for i in self.setting["tested_values"]
        ]
        self.widgets["param_value_dropdown"] = widgets.Dropdown(
            options=values,
            value=values[0],
            description="Parameter Value:",
            disabled=False,
        )
        iteration = [i for i in range(self.setting["num_runs"])]
        self.widgets["iteration_dropdown"] = widgets.Dropdown(
            options=iteration,
            value=iteration[0],
            description="Iteration Number:",
            disabled=False,
        )

        display(
            widgets.HBox(
                [
                    self.widgets["param_value_dropdown"],
                    self.widgets["iteration_dropdown"],
                ]
            )
        )

    def visualise_lob(self):
        """Creates a plot of the LOB for a specified parameter value and iteration.

        Parameter value and iteration value are chosen through use of previously
        created dropdown widgets. Function than extracts the specified LOB pd.DataFrame
        and converts into a new pd.DataFrame which can be used by visualisation methods.
        """

        df = self._extract_lob(
            param_index=self.widgets["param_value_dropdown"].index,
            iteration_index=self.widgets["iteration_dropdown"].value,
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

    def animate_lob(self):
        """Creates an animation of the LOB for a given parameter value and iteration.

        Parameter value and iteration value are chosen through use of previously
        created dropdown widgets. Function than extracts the specified LOB pd.DataFrame
        and converts into a new pd.DataFrame which can be used by visualisation methods.
        """

        df = self._extract_lob(
            param_index=self.widgets["param_value_dropdown"].index,
            iteration_index=self.widgets["iteration_dropdown"].value,
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

        param_value = self.widgets["param_value_dropdown"].value
        iteration_value = self.widgets["iteration_dropdown"].value

        fig.update_layout(
            width=800,
            height=800,
            xaxis_showgrid=True,
            yaxis_showgrid=True,
            plot_bgcolor="rgba(0,0,0,0)",
            title_text=f"LOB of Tested val {param_value, iteration_value}",
            showlegend=True,
        )

        fig.update_traces(width=0.001)
        fig.update_xaxes(title_text="Volume")
        fig.update_yaxes(title_text="Price")
        fig.show()

    @staticmethod
    def line_plot(
        ax: Axes,
        xdata: list,
        ydata: list,
        labels: list,
        formats: list = None,
        title: str = None,
        xlabel: str = None,
        ylabel: str = None,
        loc: str = "upper right",
    ) -> Axes:
        """Utility for creating a simple line plot.

        Args:
            ax (Axes):
                Handles to matplotlib Axes object to plot data in.
            xdata (list):
                List of datasets to use as x-axis data.
            ydata (list):
                List of datasets to use as y-axis data.
            labels (list):
                List of strings to use as dataset labels.
            formats (list, optional):
                List of strings to use as dataset formats. Defaults to None (lines).
            title (str, optional):
                String to use as axis title. Defaults to None (no title).
            xlabel (str, optional):
                String to use as axis xlabel. Defaults to None (no xlabel).
            ylabel (str, optional):
                String to use as axis ylabel. Defaults to None (no ylabel).
            loc (str, optional):
                Position of axes legend. Defaults to 'upper right'.

        Raises:
            ValueError: If length of xdata and ydata arguments does not match.
        """

        if len(xdata) != len(ydata):
            raise ValueError("'xdata' and 'ydata' do not have same number of datasets")
        else:
            n = len(ydata)

        if formats is None:
            formats = ["-"] * n
        for i in range(n):
            ax.plot(xdata[i], ydata[i], formats[i], label=labels[i])

        ax.legend(loc=loc)

        if title is not None:
            ax.set_title(title)
        if xlabel is not None:
            ax.set_xlabel(xlabel, labelpad=15)
        if ylabel is not None:
            ax.set_ylabel(ylabel, labelpad=15)
