import os
import logging

# ref: https://pytest-xdist.readthedocs.io/en/latest/how-to.html#creating-one-log-file-for-each-worker
def pytest_configure(config):
    path = "test_logs"
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)

    env_log_level = os.getenv('LOG_LEVEL')
    log_level = config.getini("log_file_level")
    if not env_log_level is None:
        log_level = env_log_level

    worker_id = os.environ.get("PYTEST_XDIST_WORKER")
    if worker_id is not None:
        logging.basicConfig(
            format=config.getini("log_file_format"),
            filename=f"{path}/tests_{worker_id}.test.log",
            level=log_level,
        )