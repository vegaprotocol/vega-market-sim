# DevOps

The `devops` directory contains the tools for running a pre-configured `DevOpsScenario`
class either as a simulation on a nullchain network or deployed to an existing
Vega network. Scenarios can currently be deployed to the following networks.

- stagnet1
- stagnet3
- fairground

Currently market-sim agents are unable to make governance commands on existing networks.
Therefore scenarios must be run on existing markets.
## Setup
---
### Vega-Market-Sim
To run scenario simulations, follow the
[setup instructions](https://github.com/vegaprotocol/vega-market-sim/blob/develop/README.md#setup)
instructions in the vega-market-sim `README.md`. To launch the console when running
simulations ensure the 
[UI setup instructions](https://github.com/vegaprotocol/vega-market-sim/blob/develop/README.md#ui)
have been followed.

Additionally to deploy scenarios to existing networks ensure the most-recent network
config files have been setup with the following command:

    $ make networks
### Wallet
To deploy a devops scenario to a network the user must have the latest `vegawallet`
binary and a wallet with the wallet name, wallet pass, and key names as defined
in the `wallet.py` module.

To create a new wallet:

    $ vega wallet create -w devops

To generate a new key:

    $ vega wallet key generate -w devops -m "name:market_maker"

Once the wallet is setup you must ensure each key has enough of the required asset for
your scenario. For internal-networks the `devopstools` repo has a `topup parties` script
for topping up your keys. For example:

    $ go run main.go topup parties --network stagnet1 --erc20-token-address 0x973cB2a51F83a707509fe7cBafB9206982E1c3ad  --amount 180000  --parties 673be7e0d9ea3f5e9250d6817f96cbaf62aa6f8b8d6891090ed05f078fbf0402
## Scenarios
---
### The DevOps Scenario
The `scenario.py` module contains the `DevOpsScenario` class which can be configured
for different markets. By default the scenario contains the following agents:

- 1x `ConfigurableMarketManager` agent: defines the market to deploy to or the market to create
- 1x `ExponentialShapedMarketMaker` agent: provides an order-book on the specified market
- 2x `OpenAuctionPass` agents: provide orders to meet auction exit conditions
- 3x `MarketOrderTrader` agents: provide trades at each time-step for candle data
- 5x `MomentumTrader` agents: provide realistic trading strategies in the market
- 3x `PriceSensitiveMarketOrderTrader` agents: control the market-makers position

The arguments for each agent can be passed into the scenario through the following
data classes.

- `MarketManagerArgs`
- `MarketMakerArgs`
- `AuctionTraderArgs`
- `RandomTraderArgs`
- `MomentumTraderArgs` 
- `SensitiveTraderArgs`
### Configuring Scenarios
To configure a new scenario, add a new key pair to the `SCENARIOS` dictionary in the
`registry.py` module.

When creating a scenario; control which market to operate in with the 
`MarketManagerArgs`, control the shape of the order-book with the `MarketMakerArgs`,
and control the order sizes with the `AuctionTraderArgs`, `RandomTraderArgs`,
`MomentumTraderArgs`, and `SensitiveTraderArgs`. Simulation settings can be controlled
with the `SimulationArgs`.

For more information on each args affect on a scenario refer to the module level
docstring of `parameters.py`.
### Simulating Scenarios
Before deploying a scenario to a network, it is worth running simulations to ensure
the scenario behaves as expected (i.e. market stays out of auctions, parties not 
frequently closed out, market-maker able to control it's position).

To simulate a scenario run the following command.

    $ python -m vega_sim.devops.run -c -s ETHUSD

This command will launch a locally hosted console and run the ETHUSD scenario on a
nullchain network (default option).
### Deploying Scenarios
To deploy a scenario to a network, simply define the network to run on.

    $ python -m vega_sim.devops.run -n STAGNET1 -c -s ETHUSD

This command will launch a locally hosted console and run the ETHUSD scenario on the
stagnet1 network. Currently users are able to choose between the following networks:

- STAGNET1
- STAGNET2
- STAGNET3
- FAIRGROUND
