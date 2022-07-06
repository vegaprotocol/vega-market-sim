docker run --rm \
    --mount type=bind,source=/tmp,target=/tmp \
    --mount type=bind,source=$PWD/tests,target=/vega_market_sim/tests \
    --platform linux/amd64 \
    vega_sim_test:latest pytest -v -m integration