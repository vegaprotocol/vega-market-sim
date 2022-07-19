docker rm vega_test || true
docker run \
    --platform linux/amd64 \
    --name vega_test \
    vega_sim_test:latest pytest -s -v -m integration --log-cli-level INFO
docker_status=$?
docker cp vega_test:/tmp ./test_logs/
docker rm vega_test
exit ${docker_status}