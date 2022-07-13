docker run \
    --mount type=bind,source=$PWD/tests,target=/vega_market_sim/tests \
    --platform linux/amd64 \
    --name vega_test \
    vega_sim_test:latest pytest -s -v -m integration
docker_status=$?
docker cp vega_test:/tmp ./test_logs/
docker rm vega_test
exit(docker_status)