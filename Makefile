VEGA_TAG := develop
WALLET_TAG := develop
DATA_NODE_TAG := develop
EXTERN_DIR := "./extern"

all: pull_deps build_deps

pull_deps:
	@if [ ! -d ./extern/ ]; then mkdir ./extern/; fi
	@echo "Downloading Git dependencies into " ${EXTERN_DIR}
	@echo "Downloading Vega"
	@if [ ! -d ./extern/vega ]; then mkdir ./extern/vega; git clone https://github.com/vegaprotocol/vega ${EXTERN_DIR}/vega; fi
ifneq (${VEGA_TAG},develop)
	@git -C ${EXTERN_DIR}/vega checkout -b ${VEGA_TAG}
else
	@git -C ${EXTERN_DIR}/vega checkout develop; git -C ${EXTERN_DIR}/vega pull
endif
	@echo "Downloading data-node"
	@if [ ! -d ./extern/data-node ]; then mkdir ./extern/data-node; git clone https://github.com/vegaprotocol/data-node ${EXTERN_DIR}/data-node; fi
ifneq (${DATA_NODE_TAG},develop)
	@git -C ${EXTERN_DIR}/data-node checkout -b ${DATA_NODE_TAG}
else
	@git -C ${EXTERN_DIR}/vega checkout develop; git -C ${EXTERN_DIR}/vega pull
endif
	@echo "Downloading Vegawallet"
	@if [ ! -d ./extern/vegawallet ]; then mkdir ./extern/vegawallet; git clone https://github.com/vegaprotocol/vegawallet ${EXTERN_DIR}/vegawallet; fi
ifneq (${WALLET_TAG},develop)
	@git -C ${EXTERN_DIR}/vegawallet checkout -b ${WALLET_TAG}
else
	@git -C ${EXTERN_DIR}/vegawallet checkout develop; git -C ${EXTERN_DIR}/vegawallet pull
endif

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
