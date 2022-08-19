# Vega Market Simulator

Build and interact with a self-contained Vega chain, with controllable passage of time.

The market simulator aims to:
 - Allow you to easily spin up and control a light 'null blockchain' implementation of the Vega stack, including a wallet and faucet.
   - This environment starts with a minimal set of information, but allows creation of arbitrary parties with controllable funds, and manages public key/token interaction simply for the user.
 - Provides a simple Python wrapper over the most frequently used functionality, aiming to stay stable even under changes in the underlying gRPC/REST Vega API.
 - Continues to expose everything required to build more complex function calls to the Vega system itself.
 - Dynamically assigns ports to the various Vega services and links them together. 
   - This allows multiple Vega market simulators to run alongside each other on the same box without interfering with one another.


Market Simulator is still under active development and so may change notably over time.


## Setup

For the most part the package is fairly self-contained Python, however there are some utility functions which will automatically download the requisite Vega services for you. The full set of steps would then be:
  - Clone the repository to your local drive
  - Install the latest version of [Golang](https://go.dev)
  - Run `make` to automatically pull install dependencies
    - If you have your own instances of the various service to run from elsewhere, you can skip this step
  - Install the package into your local environment. 
    - The process for this will vary depending upon your package manager of choice. We provide here a full Poetry `pyproject.toml` and a `requirements.txt` which is derived from it. These are kept in sync through a check on all pull requests.
 -  Then run your environment.

### Setup if you're using `conda` as your python package manager

1. Create a new conda environment, perhaps call it `sim` as in `conda create -n sim python=3.10`. 
2. Activate the new environment `conda activate sim` 
3. Clone the repo into `mypath/vega-market-sim` and run `make` there. 
4. Use `conda install --file requirements.txt`.
5. Run `pytest -s tests/integration/test_trading.py` from `mypath/vega-market-sim`. This should pass; if not one of the steps above didn't work.
6. If you now want to be able to use the `vega-market-sim` even from other directories, run `conda develop mypath/vega-market-sim`. 
7. Optional: to have UI, run `make ui`. 



### UI

Building the console UI is not a necessary component, but can be useful for visualising the state of the Vega service. In order to do this:
  - Ensure you have `yarn` installed
  - Ensure you are running node v16. If you use other versions in general, `nvm` can be useful to switch to v14 without wiping your other version
  - Run `make ui`, which will download the requisite repository and install it into the `/extern` directory
  - Set the `run_with_console` flag to `True` when creating the `VegaServiceNull` class

## Basic use

Examples can be found within the `/examples` folder. A good one to start is `/examples/nullchain.py` which spins up a simple service and proposes a market.


## Decimal Handling

For the most part the simulator aims to shield you from the specifics of running the market on a blockchain, however decimal handling is one place where you may have to be (hopefully only slightly) aware of what's going on.
In order to avoid the imprecision issues with floating point numbers, along with aligning with how Ethereum handles the issue, stored numbers in the Vega chain are generally saved as ints, padded with zeros to represent the
number of decimal places the number has. For example, 10 with two decimal places would be saved as 1000, whilst 10.52 would become 1052. Whilst this obviously limits precision to a set level (there can be no 10.521 in the 
two decimal place world) it allows the numbers to be stored exactly.

Alongside these, there is also a field for the number of decimal places a given asset's price, or market's price and position, is stored in. This allows conversion back to a floating point number when desired.

Many fields, especially those returning a single number, run this conversion for you. As do all those taking a number as input. Where one has to be more careful is in more complex objects which may have such numbers nested
inside them in unknown locations.

To help with this differentiation, all functions which may return such an object should be carved out into the `data_raw` module within the `api` path, as opposed to the standard `data` module. 
If you're just using the Service interface (as hopefully is generally sufficient) then there is an additional layer of defence, the `warn_on_raw_data_access` flag. This flag will trigger the module to 
warn log every time a method which returns something which could/does contain these integers is called. It's then up to the external code to handle this information (or ignore it if you know you are safe). 

Once code has been written, this flag can be turned off for production runs so as not to flag erroneously.


### Reinforcement Learning

The nascent framework for reinforcement learning applications of the Vega Market Sim can be found within `vega_sim.reinforcement`, this includes the beginnings of a 'background market' within the folder `vega_sim.reinforcement.full_market_sim`
alongside an agent in `vega_sim.reinforcement.learning_agent` which learns from a currently very simple set of inputs (alongside an input of a future price, to make learning on a random walk possible at all!) Usage is new, and the code strucure
and functionality is liable to change *significantly* in the future, however input is welcomed.
