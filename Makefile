VEGA_TAG := develop
WALLET_TAG := develop
DATA_NODE_TAG := develop
CONSOLE_TAG := master
PROTO_TAG := develop
EXTERN_DIR := "./extern"

all: pull_deps build_deps

ui: pull_deps_ui build_deps_ui

pull_deps:
	@if [ ! -d ./extern/ ]; then mkdir ./extern/; fi
	@echo "Downloading Git dependencies into " ${EXTERN_DIR}
	@echo "Downloading Vega"
	@if [ ! -d ./extern/vega ]; then mkdir ./extern/vega; git clone https://github.com/vegaprotocol/vega ${EXTERN_DIR}/vega; fi
ifneq (${VEGA_TAG},develop)
	@git -C ${EXTERN_DIR}/vega pull; git -C ${EXTERN_DIR}/vega checkout ${VEGA_TAG}
else
	@git -C ${EXTERN_DIR}/vega checkout develop; git -C ${EXTERN_DIR}/vega pull
endif
	@echo "Downloading data-node"
	@if [ ! -d ./extern/data-node ]; then mkdir ./extern/data-node; git clone https://github.com/vegaprotocol/data-node ${EXTERN_DIR}/data-node; fi
ifneq (${DATA_NODE_TAG},develop)
	@git -C ${EXTERN_DIR}/data-node pull; git -C ${EXTERN_DIR}/data-node checkout ${DATA_NODE_TAG}
else
	@git -C ${EXTERN_DIR}/vega checkout develop; git -C ${EXTERN_DIR}/vega pull
endif
	@echo "Downloading Vegawallet"
	@if [ ! -d ./extern/vegawallet ]; then mkdir ./extern/vegawallet; git clone https://github.com/vegaprotocol/vegawallet ${EXTERN_DIR}/vegawallet; fi
ifneq (${WALLET_TAG},develop)
	@git -C ${EXTERN_DIR}/vegawallet pull; git -C ${EXTERN_DIR}/vegawallet checkout ${WALLET_TAG}
else
	@git -C ${EXTERN_DIR}/vegawallet checkout develop; git -C ${EXTERN_DIR}/vegawallet pull
endif

build_deps:
	@mkdir -p ./vega_sim/bin
	cd ${EXTERN_DIR}/vega && go build -o ../../vega_sim/bin/ ./...
	cd ${EXTERN_DIR}/vegawallet && go build -o ../../vega_sim/bin/ ./...
	cd ${EXTERN_DIR}/data-node && go build -o ../../vega_sim/bin/ ./...

pull_deps_ui:
	@if [ ! -d ./extern/ ]; then mkdir ./extern/; fi
	@echo "Downloading Git dependencies into " ${EXTERN_DIR}
	@echo "Downloading Vega slimline console"
	@if [ ! -d ./extern/console ]; then mkdir ./extern/console; git clone https://github.com/vegaprotocol/slimline-console ${EXTERN_DIR}/console; fi
ifneq (${CONSOLE_TAG},master)
	@git -C ${EXTERN_DIR}/console pull; git -C ${EXTERN_DIR}/console checkout ${CONSOLE_TAG}
else
	@git -C ${EXTERN_DIR}/console checkout master; git -C ${EXTERN_DIR}/console pull
endif

build_deps_ui:
	@mkdir -p ./vega_sim/bin/console
	@rsync -av ${EXTERN_DIR}/console vega_sim/bin/ --exclude ${EXTERN_DIR}/console/.git
	@yarn --cwd vega_sim/bin/console install

pull_deps_proto:
	@if [ ! -d ./extern/ ]; then mkdir ./extern/; fi
	@echo "Downloading Git dependencies into " ${EXTERN_DIR}
	@echo "Downloading Vega Protos"
	@if [ ! -d ./extern/proto ]; then mkdir ${EXTERN_DIR}/proto; git clone https://github.com/vegaprotocol/protos ${EXTERN_DIR}/proto; fi
ifneq (${PROTO_TAG},develop)
	@git -C ${EXTERN_DIR}/proto pull; git -C ${EXTERN_DIR}/proto checkout ${PROTO_TAG}
else
	@git -C ${EXTERN_DIR}/proto checkout develop; git -C ${EXTERN_DIR}/proto pull
endif

build_proto:
	@rm -rf ./vega_sim/proto
	@mkdir ./vega_sim/proto
	@python -m grpc_tools.protoc -I ${EXTERN_DIR}/proto/sources --python_out=vega_sim/proto --grpc_python_out=vega_sim/proto $(shell find ${EXTERN_DIR}/proto/sources -name '*.proto')
	@GENERATED_DIR=./vega_sim/proto scripts/post-generate.sh

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
