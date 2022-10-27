import copy
import csv
import json
import os
import pathlib
from dataclasses import dataclass
from random import random
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from vega_sim.null_service import VegaServiceNull
from vega_sim.scenario.scenario import Scenario

from vega_sim.api.market import MarketConfig

PARAMETER_AMEND_WALLET = ("param", "amend")

FILE_PATTERN = "NETP_{param_name}_{param_value}.csv"
FILE_PATTERN_LOB = "NETP_{param_name}_{param_value}_LOB.csv"
OUTPUT_DIR = "parameter_results"


@dataclass
class Experiment:
    name: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
        }


@dataclass
class SingleParameterExperiment(Experiment):
    parameter_to_vary: str
    values: List[str]
    scenario: Scenario
    runs_per_scenario: int = 1
    additional_parameters_to_set: Optional[Dict[str, str]] = None
    data_extraction: List[Tuple] = None
    market_parameter: Optional[bool] = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "parameter_tested": self.parameter_to_vary,
            "tested_values": self.values,
            "scenario": self.scenario.__class__.__name__,
            "num_runs": self.runs_per_scenario,
            "additional_parameters": self.additional_parameters_to_set,
            "data_extraction": self.data_extraction,
        }


def _run_parameter_iteration(
    scenario: Scenario,
    parameter_to_vary: str,
    value: str,
    additional_parameters_to_set: Optional[Dict[str, str]] = None,
    random_state: Optional[np.random.RandomState] = None,
) -> Any:
    with VegaServiceNull(
        warn_on_raw_data_access=False,
        retain_log_files=True,
        run_with_console=False,
        transactions_per_block=100,
        use_full_vega_wallet=False,
    ) as vega:
        vega.create_wallet(*PARAMETER_AMEND_WALLET)
        vega.mint(
            PARAMETER_AMEND_WALLET[0],
            asset="VOTE",
            amount=1e4,
        )

        if additional_parameters_to_set is not None:
            for param, new_value in additional_parameters_to_set.items():
                vega.update_network_parameter(
                    PARAMETER_AMEND_WALLET[0], parameter=param, new_value=new_value
                )

        vega.update_network_parameter(
            PARAMETER_AMEND_WALLET[0], parameter=parameter_to_vary, new_value=value
        )

        res = scenario.run_iteration(vega=vega, random_state=random_state)

        return res


def _run_market_parameter_iteration(
    scenario: Scenario,
    parameter_to_vary: str,
    value: Union[str, int, float],
    random_state: Optional[np.random.RandomState],
) -> Any:

    with VegaServiceNull(
        warn_on_raw_data_access=False,
        retain_log_files=True,
        run_with_console=False,
        transactions_per_block=100,
        use_full_vega_wallet=False,
    ) as vega:

        market_config = MarketConfig("default")

        market_config.set(parameter_to_vary, value)

        res = scenario.run_iteration(
            vega=vega,
            random_state=random_state,
            market_config=market_config,
        )

        return res


def run_single_parameter_experiment(
    experiment: SingleParameterExperiment,
) -> Dict[str, List[Any]]:
    results = {}
    random_seeds = [
        np.random.RandomState(i) for i in range(experiment.runs_per_scenario)
    ]
    for value in experiment.values:
        results[value] = []
        for state in copy.deepcopy(random_seeds):
            if experiment.market_parameter:
                res = _run_market_parameter_iteration(
                    scenario=experiment.scenario,
                    parameter_to_vary=experiment.parameter_to_vary,
                    value=value,
                    random_state=state,
                )
            else:
                res = _run_parameter_iteration(
                    scenario=experiment.scenario,
                    parameter_to_vary=experiment.parameter_to_vary,
                    value=value,
                    random_state=state,
                )
            results[value].append(res)

    return results


def output_logs(
    results: Dict[str, List[List[Tuple[List[Any], Dict[str, Any]]]]],
    parameter_name: str,
    experiment: Experiment,
    file_pattern: Optional[str] = FILE_PATTERN,
    result_folder: Optional[str] = None,
    col_ordering: Optional[List[str]] = None,
    config_json: bool = True,
):
    result_folder = result_folder or OUTPUT_DIR
    final_folder = pathlib.Path(result_folder) / experiment.name
    os.makedirs(final_folder, exist_ok=True)

    if config_json:
        with open(final_folder / "run_config.json", "w") as f:
            json.dump(experiment.to_dict(), f, indent=4, sort_keys=True)

    if experiment.data_extraction is None:
        for value, result_list in results.items():
            file_path = final_folder / file_pattern.format(
                param_name=parameter_name, param_value=value
            )
        with open(file_path, "w") as f:
            csv_writer = csv.writer(f, delimiter=",")
            headers = (
                list(result_list[0][0].keys()) if col_ordering is None else col_ordering
            )
            csv_writer.writerow(["Iteration"] + headers)
            for i, res in enumerate(result_list):
                for row in res:
                    csv_writer.writerow([i] + [row[c] for c in headers])
    else:
        for value, result_list in results.items():
            for data_extraction in experiment.data_extraction:
                file_path = final_folder / data_extraction[0].format(
                    param_name=parameter_name, param_value=value
                )
                with open(file_path, "w") as f:
                    csv_writer = csv.writer(f, delimiter=",")
                    csv_writer.writerow(["Iteration"] + data_extraction[1])
                    for i, res in enumerate(result_list):
                        for row in res:
                            csv_writer.writerow(
                                [i] + [row[c] for c in data_extraction[1]]
                            )
