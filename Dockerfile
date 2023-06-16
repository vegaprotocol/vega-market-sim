FROM golang:1.19-buster AS gobuild
COPY ./extern /extern
WORKDIR /extern
RUN mkdir /extern/bin
RUN ls -l
RUN cd ./vega && CGO_ENABLED=0 go build -o ../bin/ ./... && cd ..
RUN cd ./vegacapsule && go build -o ../bin/ ./... && cd ..
ENV PATH="/vega_market_sim/vega_sim/bin:${PATH}"

FROM python:3.10-slim-bullseye AS vegasim_base
RUN useradd -ms /bin/bash vega
WORKDIR /vega_market_sim
RUN mkdir vega_sim
COPY --from=gobuild /extern/bin ./vega_sim/bin
COPY ./requirements.txt .
RUN  pip install -r requirements.txt

FROM vegasim_base AS vegasim
COPY ./tests ./tests
COPY ./vega_sim ./vega_sim
COPY ./pyproject.toml ./pyproject.toml
RUN pip install -e . --no-deps 
RUN chmod 777 /vega_market_sim
USER vega

FROM vegasim_base AS vegasim_test
COPY ./requirements-dev.txt .
COPY ./requirements-learning.txt .
RUN  pip install -r requirements-dev.txt
RUN  pip install -r requirements-learning.txt
COPY pytest.ini .
COPY ./tests ./tests
COPY ./vega_sim ./vega_sim
COPY ./examples ./examples
COPY ./pyproject.toml ./pyproject.toml
RUN pip install -e .
RUN chmod 777 /vega_market_sim
USER vega

FROM vegasim_base AS vegasim_learning
COPY ./requirements-learning.txt .
RUN  pip install -r requirements-learning.txt
COPY ./pyproject.toml ./pyproject.toml
COPY ./tests ./tests
COPY ./vega_sim ./vega_sim
RUN pip install -e .
RUN chmod 777 /vega_market_sim
USER vega
