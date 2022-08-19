container_name="vega_test$1"

docker rm ${container_name} || true
docker run \
    --platform linux/amd64 \
    --name ${container_name} \
    --mount type=bind,source=/tmp,target=/tmp \
    --mount type=bind,source=/Users/tom/Code/vega-market-sim/tests,target=/vega_market_sim/tests \
    vega_sim_test:latest pytest -s -v -m integration --log-cli-level INFO tests/integration/test_openoracle_settlement.py
docker_status=$?
docker cp ${container_name}:/tmp ./test_logs/
docker rm ${container_name}
exit ${docker_status}