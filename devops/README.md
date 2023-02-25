# DevOps

The `devops` directory contains the tools for running pre-configured scenarios or individual pre-configured agents either as a simulation on a nullchain network or deployed to an existing Vega network. Scenarios can currently be deployed to the following networks.

- stagnet1
- stagnet3
- fairground

Currently market-sim agents are unable to make governance commands on existing networks. Therefore scenarios must be run on existing markets.
## Setup
### Vega-Market-Sim
To run scenario simulations, follow the [setup instructions](https://github.com/vegaprotocol/vega-market-sim/blob/develop/README.md#setup) instructions in the vega-market-sim `README.md`. To launch the console when running simulations ensure the [UI setup instructions](https://github.com/vegaprotocol/vega-market-sim/blob/develop/README.md#ui) have been followed.

Additionally to deploy scenarios to existing networks ensure the most-recent network config files have been setup with the following command:
```bash
$ make networks
```

### Wallet Setup
To run a scenario or agent on an existing vega network, a vega wallet must be setup with long-living API tokens initialised and created for the wallet.

1.  Create a wallet:

    ```bash
    $ vega wallet create --wallet-nam MY_VEGA_WALLET_NAME
    ```

1. Set an environment variable for your wallet name:

    ```
    export VEGA_USER_WALLET_NAME=MY_VEGA_WALLET_NAME
    ```

1. Initialise long-living API tokens:

    ```bash
    $ vega wallet api-token init
    ```

1. Create a `.text` file containing the chosen tokens-passphrase:

    ```text
    MY_VEGA_TOKENS_PASSPHRASE
    ```

1. Set an environment variable for the path to the `.text` file (this path can be relative to your `vega-market-sim` directory):

    ```bash
    $ export VEGA_WALLET_TOKENS_PASSPHRASE_FILE=/path/to/file.text
    ```

1. Generate an API token for the specific wallet:

    ```bash
    $ vega wallet api-token generate --wallet-name MY_VEGA_WALLET_NAME
    ```

1. Create a `.json` file with the following format:

    ```json
    {
        "MY_VEGA_WALLET_NAME": "MY_VEGA_TOKEN",
    }
    ```

1. Set an environment variable for the path to the `.json` file (this path can be relative to your `vega-market-sim` directory):

    ```bash
    export VEGA_WALLET_TOKENS_FILE=/path/to/file.json
    ```

### Key Setup:

To run a devops scenario, the wallet must contain keys with the specific key names listed in the [wallet.py](./wallet.py) module. To run a single agent there is no requirement to use specific key names.

1. Create new keys with specific key names:

    ```bash
        $ vega wallet key generate -w MY_VEGA_WALLET_NAME -m "name:MY_VEGA_KEY_NAME"
    ```

1. Once the keys are setup they must be topped up with the assets needed for the scenario. For internal-networks the `devopstools` repo has a `topup parties` script for topping up your keys:

    ```bash
        $ go run main.go topup parties --network stagnet1 --erc20-token-address ERC_20_TOKEN_ADDRESS  --amount 180000  --parties MY_VEGA_PUBLIC_KEY
    ```

## Scenarios
### Simulating Scenarios
Before deploying a scenario to a network, it is worth running simulations to ensure
the scenario behaves as expected (i.e. market stays out of auctions, parties not 
frequently closed out, market-maker able to control it's position).

To simulate a scenario run the following command:

```bash
$ python -m devops.run_scenario -s SCENARIO_NAME -c
```

### Deploying Scenarios

To deploy a scenario to a network, simply define the network and market to deploy too:

```bash
$ python -m devops.run_scenario -n NETWORK_NAME -s SCENARIO_NAME -m MARKET_NAME
```

## Agents

### Simulating Agents

Before deploying an agent to a network, it can be tested in a specific scenario to see how it behaves.

To simulate an agent run the following command:

```bash
$ python -m devops.run_agent -a AGENT_NAME -s SCENARIO_NAME
```
### Deploying Agents

to deploy the agent to a network, define the agent to deploy, the key to use, and the network and market to deploy too:

```
$ python -m devops.run_agent -a AGENT_NAME -k MY_VEGA_KEY_NAME -n NETWORK_NAME -m MARKET_NAME