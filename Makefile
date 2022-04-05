VEGA_TAG := tags/v0.49.9-pre3
WALLET_TAG := tags/v0.13.2
DATA_NODE_TAG := tags/v0.49.3
EXTERN_DIR := "./extern"

all: pull_deps build_deps

pull_deps:
	@mkdir -p ./extern/{vega,vegawallet,data-node}
	@echo "Downloading Git dependencies into " ${EXTERN_DIR}
	@echo "Downloading Vega"
	@git clone https://github.com/vegaprotocol/vega ${EXTERN_DIR}/vega && git -C ${EXTERN_DIR}/vega checkout -b ${VEGA_TAG}
	@echo "Downloading data-node"
	@git clone https://github.com/vegaprotocol/data-node ${EXTERN_DIR}/data-node && git -C ${EXTERN_DIR}/data-node checkout -b ${DATA_NODE_TAG}
	@echo "Downloading Vegawallet"
	@git clone https://github.com/vegaprotocol/vegawallet ${EXTERN_DIR}/vegawallet && git -C ${EXTERN_DIR}/vegawallet checkout -b ${WALLET_TAG}

build_deps:
	@mkdir -p ./vega_sim/bin
	cd ${EXTERN_DIR}/vega && go build -o ../../vega_sim/bin/ ./...
	cd ${EXTERN_DIR}/vegawallet && go build -o ../../vega_sim/bin/ ./...
	cd ${EXTERN_DIR}/data-node && go build -o ../../vega_sim/bin/ ./...

.PHONY: black
black:
	@black .

.PHONY: blackcheck
blackcheck:
	@black --check .

.PHONY: clean
clean:
	@rm -rf "$(GENERATED_DIR)"

.PHONY: flake8
flake8:
	@flake8

.PHONY: test
test:
	@pipenv --bare install --dev # 1>/dev/null 2>&1
	@pipenv run pip install -e .
	@env PYTHONPATH=. pipenv run pytest tests/
