FROM python:3.10-slim-bullseye AS vegasim

ARG vega_path
ARG wallet_path
ARG data_node_path

WORKDIR /vega_market_sim

COPY ./vega_sim ./vega_sim
COPY ./tests ./tests

COPY $vega_path ./vega_sim/bin
COPY $wallet_path ./vega_sim/bin
COPY $data_node_path ./vega_sim/bin

