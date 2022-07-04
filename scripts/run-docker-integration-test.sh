docker run --rm \
    --mount type=bind,source=$PWD/vega_sim/bin/data-node,target=/vega_market_sim/vega_sim/bin/data-node \
    --mount type=bind,source=$PWD/vega_sim/bin/vega,target=/vega_market_sim/vega_sim/bin/vega \
    --mount type=bind,source=$PWD/vega_sim/bin/vegawallet,target=/vega_market_sim/vega_sim/bin/vegawallet \
    --mount type=bind,source=/tmp,target=/tmp \
    --mount type=bind,source=$PWD/tests,target=/vega_market_sim/tests \
    --platform linux/amd64 \
    vega_sim_test:latest pytest -v -m integration