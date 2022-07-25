import csv
from dataclasses import dataclass
import json
import os
from typing import Any, Dict, List, Optional, Tuple
import pathlib

from vega_sim.scenario.scenario import Scenario
from vega_sim.null_service import VegaServiceNull


PARAMETER_AMEND_WALLET = ("param", "amend")

FILE_PATTERN = "NETP_{param_name}_{param_value}.csv"
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "parameter_tested": self.parameter_to_vary,
            "tested_values": self.values,
            "scenario": self.scenario.__class__.__name__,
            "num_runs": self.runs_per_scenario,
            "additional_parameters": self.additional_parameters_to_set,
        }


def _run_parameter_iteration(
    scenario: Scenario,
    parameter_to_vary: str,
    value: str,
    additional_parameters_to_set: Optional[Dict[str, str]] = None,
) -> Any:
    with VegaServiceNull(warn_on_raw_data_access=False, retain_log_files=True) as vega:
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

        return scenario.run_iteration(vega=vega)


def run_single_parameter_experiment(
    experiment: SingleParameterExperiment,
) -> Dict[str, List[Any]]:
    results = {}
    for value in experiment.values:
        results[value] = []
        for _ in range(experiment.runs_per_scenario):
            results[value].append(
                _run_parameter_iteration(
                    scenario=experiment.scenario,
                    parameter_to_vary=experiment.parameter_to_vary,
                    value=value,
                )
            )
    return results


def output_logs(
    results: Dict[str, List[List[Tuple[List[Any], Dict[str, Any]]]]],
    parameter_name: str,
    experiment: Experiment,
    result_folder: Optional[str] = None,
    col_ordering: Optional[List[str]] = None,
):
    result_folder = result_folder or OUTPUT_DIR
    final_folder = pathlib.Path(result_folder) / experiment.name
    os.makedirs(final_folder, exist_ok=True)

    with open(final_folder / "run_config.json", "w") as f:
        json.dump(experiment.to_dict(), f, indent=4, sort_keys=True)

    for value, result_list in results.items():
        file_path = final_folder / FILE_PATTERN.format(
            param_name=parameter_name, param_value=value
        )
        with open(file_path, "w") as f:
            csv_writer = csv.writer(f, delimiter=",")
            # Keys should not change throughout, so just take the first
            headers = (
                list(result_list[0][0].keys()) if col_ordering is None else col_ordering
            )

            csv_writer.writerow(["Iteration"] + headers)
            for i, res in enumerate(result_list):
                for row in res:
                    csv_writer.writerow([i] + [row[c] for c in headers])
