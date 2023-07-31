import os
import logging


# ref: https://pytest-xdist.readthedocs.io/en/latest/how-to.html#creating-one-log-file-for-each-worker
def pytest_configure(config):
    path = "test_logs"
    if not os.path.exists(path):
        os.makedirs(path)

    worker_id = os.environ.get("PYTEST_XDIST_WORKER")
    if worker_id is not None:
        logging.basicConfig(
            format=config.getini("log_file_format"),
            filename=f"{path}/tests_{worker_id}.test.log",
            level=os.getenv("LOG_LEVEL", config.getini("log_file_level")),
        )
