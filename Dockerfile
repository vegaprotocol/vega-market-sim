FROM golang:1.19-buster AS gobuild

COPY ./extern /extern
WORKDIR /extern
RUN mkdir /extern/bin
RUN ls -l
RUN cd ./vega && CGO_ENABLED=0 go build -o ../bin/ ./... && cd ..

FROM python:3.10-slim-bullseye AS vegasim_base

RUN useradd -ms /bin/bash vega

WORKDIR /vega_market_sim

COPY ./requirements.txt .

RUN mkdir vega_sim
COPY --from=gobuild /extern/bin ./vega_sim/bin
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
