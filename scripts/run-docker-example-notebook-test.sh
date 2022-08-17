docker run --rm \
    --platform linux/amd64 \
    # --mount type=bind,source=/Users/tom/Code/vega-market-sim/examples,target=/vega_market_sim/examples \
    # --mount type=bind,source=/tmp,target=/tmp \
    vega_sim_test:latest pytest --log-cli-level INFO --nbmake examples/notebooks/Settlement.ipynb