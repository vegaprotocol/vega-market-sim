FROM python:3.10-slim-bullseye AS vegasim_base

RUN useradd -ms /bin/bash vega

WORKDIR /vega_market_sim

COPY ./requirements.txt .

COPY ./tests ./tests
COPY ./vega_sim ./vega_sim

FROM vegasim_base AS vegasim

RUN  pip install -r requirements.txt

FROM vegasim_base AS vegasim_test

COPY pytest.ini .

COPY ./requirements-dev.txt .
RUN  pip install -r requirements-dev.txt

COPY ./examples ./examples
COPY ./pyproject.toml ./pyproject.toml

RUN pip install -e .

USER vega