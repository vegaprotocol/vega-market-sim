#!/usr/bin/env bash

poetry run python -m vega_sim.scenario.fuzzed_markets.run_fuzz_test --steps $1
