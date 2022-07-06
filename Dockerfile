FROM golang:1.18-buster AS gobuild

COPY ./extern /extern
WORKDIR /extern
RUN mkdir /extern/bin
RUN cd ./vega && CGO_ENABLED=0 go build -o ../bin/ ./...
RUN cd ./data-node && CGO_ENABLED=0 go build -o ../bin/ ./...

FROM python:3.10-slim-bullseye AS vegasim

RUN useradd -ms /bin/bash vega

WORKDIR /vega_market_sim

COPY ./requirements.txt .
RUN  pip install -r requirements.txt

RUN mkdir vega_sim
COPY --from=gobuild /extern/bin ./vega_sim/bin
COPY ./tests ./tests
COPY ./vega_sim ./vega_sim

FROM vegasim AS vegasim_test

COPY pytest.ini .


RUN pip install pytest requests-mock

USER vega