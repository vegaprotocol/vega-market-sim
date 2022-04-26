# Vega Market Simulator

Build and interact with a self-contained Vega chain, with controllable passage of time.

The market simulator aims to:
 - Allow you to easily spin up and control a light 'null blockchain' implementation of the Vega stack, including a wallet and faucet.
   - This environment starts with a minimal set of information, but allows creation of arbitrary parties with controllable funds, and manages public key/token interaction simply for the user.
 - Provides a simple Python wrapper over the most frequently used functionality, aiming to stay stable even under changes in the underlying gRPC/REST Vega API.
 - Continues to expose everything required to build more complex function calls to the Vega system itself.
 - Dynamically assigns ports to the various Vega services and links them together. 
   - This allows multiple Vega market simulators to run alongside each other on the same box without interfering with one another.


## Setup

For the most part the package is fairly self-contained Python, however there are some utility functions which will automatically download the requisite Vega services for you. The full set of steps would then be:
  - Clone the repository to your local drive
  - Run `make` to automatically pull install dependencies
    - If you have your own instances of the various service to run from elsewhere, you can skip this step
  - Install the package into your local environment. 
    - The process for this will vary depending upon your package manager of choice, but to use pipenv as an example one would run
    -  `pipenv install /path/from/pipenv/to/vega-market-sim`
 -  Then run your environment

### UI

Building the console UI is not a necessary component, but can be useful for visualising the state of the Vega service. In order to do this:
  - Ensure you have `yarn` installed
  - Ensure you are running node v14. If you use other versions in general, `nvm` can be useful to switch to v14 without wiping your other version
  - Run `make ui`, which will download the requisite repository and install it into the `/extern` directory
  - Set the `run_wallet_with_console` flag to `True` when creating the `VegaServiceNull` class

## Basic use

Examples can be found within the `/examples` folder. A good one to start is `/examples/nullchain.py` which spins up a simple service and proposes a market.