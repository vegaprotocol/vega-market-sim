FROM python:3.10-slim-bullseye AS vegasim

WORKDIR /vega_market_sim

COPY ./requirements.txt .
RUN  pip install -r requirements.txt

COPY ./tests ./tests
COPY ./vega_sim ./vega_sim

FROM vegasim AS vegasim_test

COPY pytest.ini .

RUN pip install pytest requests-mock
