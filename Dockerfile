FROM python:3.10-slim-bullseye AS vegasim

RUN useradd -ms /bin/bash vega

WORKDIR /vega_market_sim

COPY ./requirements.txt .
RUN  pip install -r requirements.txt

COPY ./tests ./tests
COPY ./vega_sim ./vega_sim

FROM vegasim AS vegasim_test

COPY pytest.ini .

COPY ./requirements-dev.txt .
COPY ./examples ./examples
RUN  pip install -r requirements-dev.txt

USER vega