#!/usr/bin/env bash

pytest --junitxml /tmp/notebook-test-results.xml --log-cli-level INFO --nbmake examples/notebooks
