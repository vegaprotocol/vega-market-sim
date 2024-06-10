include .env
export

EXTERN_DIR := "./extern"

all: pull_deps build_deps

ui: pull_deps_ui build_deps_ui

networks: pull_deps_networks build_deps_networks

capsule: pull_deps_capsule build_deps_capsule

clean_ui:
	@echo "Deleting $(EXTERN_DIR)/console and ./vega_sim/bin/console" 
	@rm -rf "$(EXTERN_DIR)/console"
	@rm -rf "./vega_sim/bin/console"

pull_deps:
	@if [ ! -d ./extern/ ]; then mkdir ./extern/; fi
	@echo "Downloading Git dependencies into " ${EXTERN_DIR}
	@echo "Downloading Vega"
	@if [ ! -d ./extern/vega ]; then mkdir ./extern/vega; git clone https://github.com/vegaprotocol/vega ${EXTERN_DIR}/vega; fi
ifneq (${VEGA_SIM_VEGA_TAG},develop)
	@git -C ${EXTERN_DIR}/vega pull; git -C ${EXTERN_DIR}/vega checkout ${VEGA_SIM_VEGA_TAG}
else
	@git -C ${EXTERN_DIR}/vega checkout develop; git -C ${EXTERN_DIR}/vega pull
endif

build_deps:
	@mkdir -p ./vega_sim/bin
	cd ${EXTERN_DIR}/vega && go build -o ../../vega_sim/bin/ ./...

pull_deps_ui:
	@if [ ! -d ./extern/ ]; then mkdir ./extern/; fi
	@echo "Downloading Git dependencies into " ${EXTERN_DIR}
	@echo "Downloading Vega console"
	@if [ ! -d ./extern/console ]; then mkdir ./extern/console; git clone https://github.com/vegaprotocol/frontend-monorepo.git ${EXTERN_DIR}/console; fi
ifneq (${VEGA_SIM_CONSOLE_TAG},master)
	@git -C ${EXTERN_DIR}/console pull; git -C ${EXTERN_DIR}/console checkout ${VEGA_SIM_CONSOLE_TAG}
else
	@git -C ${EXTERN_DIR}/console checkout master; git -C ${EXTERN_DIR}/console pull
endif

build_deps_ui:
	@mkdir -p ./vega_sim/bin/console
	@rsync -av ${EXTERN_DIR}/console vega_sim/bin/ --exclude ${EXTERN_DIR}/console/.git
	@yarn --cwd vega_sim/bin/console install

pull_deps_networks:
	@if [ ! -d ./extern/ ]; then mkdir ./extern/; fi
	@echo "Downloading Git dependencies into " ${EXTERN_DIR}
	@echo "Downloading Vega networks-internal"
	@if [ ! -d ./extern/networks-internal ]; then mkdir ./extern/networks-internal; git clone https://github.com/vegaprotocol/networks-internal ${EXTERN_DIR}/networks-internal; fi
ifneq (${VEGA_SIM_NETWORKS_INTERNAL_TAG},develop)
	@git -C ${EXTERN_DIR}/networks-internal pull; git -C ${EXTERN_DIR}/networks-internal checkout ${VEGA_SIM_NETWORKS_INTERNAL_TAG}
else
	@git -C ${EXTERN_DIR}/networks-internal checkout develop; git -C ${EXTERN_DIR}/networks-internal pull
endif
	@if [ ! -d ./extern/networks ]; then mkdir ./extern/networks; git clone https://github.com/vegaprotocol/networks ${EXTERN_DIR}/networks; fi
ifneq (${VEGA_SIM_NETWORKS_TAG},develop)
	@git -C ${EXTERN_DIR}/networks pull; git -C ${EXTERN_DIR}/networks checkout ${VEGA_SIM_NETWORKS_TAG}
else
	@git -C ${EXTERN_DIR}/networks checkout develop; git -C ${EXTERN_DIR}/networks pull
endif

build_deps_networks:
	@mkdir -p ./vega_sim/bin/networks-internal
	@rsync -av ${EXTERN_DIR}/networks-internal vega_sim/bin/ --exclude ${EXTERN_DIR}/networks-internal/.git
	@mkdir -p ./vega_sim/bin/networks
	@rsync -av ${EXTERN_DIR}/networks vega_sim/bin/ --exclude ${EXTERN_DIR}/networks/.git

pull_deps_capsule:
	@if [ ! -d ./extern/ ]; then mkdir ./extern/; fi
	@echo "Downloading Git dependencies into " ${EXTERN_DIR}
	@echo "Downloading Vega vegacapsule"
	@if [ ! -d ./extern/vegacapsule ]; then mkdir ./extern/vegacapsule; git clone https://github.com/vegaprotocol/vegacapsule ${EXTERN_DIR}/vegacapsule; fi
ifneq (${VEGA_SIM_CAPSULE_TAG},main)
	@git -C ${EXTERN_DIR}/vegacapsule pull; git -C ${EXTERN_DIR}/vegacapsule checkout ${VEGA_SIM_CAPSULE_TAG}
else
	@git -C ${EXTERN_DIR}/vegacapsule checkout main; git -C ${EXTERN_DIR}/vegacapsule pull
endif

build_deps_capsule:
	@mkdir -p ./vega_sim/bin
	cd ${EXTERN_DIR}/vegacapsule && go build -o ../../vega_sim/bin/ ./...

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
	@env PYTHONPATH=. pytest -m "not integration and not api" tests/

.PHONY: test_api
test_api:
	@env PYTHONPATH=. pytest -m api tests/

.PHONY: test_integration
test_integration:
	@env PYTHONPATH=. pytest -m integration tests/

.PHONY: test_examples
test_examples:
	@env PYTHONPATH=. pytest --nbmake examples/notebooks/

export_reqs:
	@poetry export  --without-hashes -f requirements.txt -o requirements.txt
	@poetry export  --without-hashes -f requirements.txt --with dev -o requirements-dev.txt
	@poetry export  --without-hashes -f requirements.txt --with dev -E learning -o requirements-learning.txt