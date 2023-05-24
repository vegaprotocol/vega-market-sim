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

### **MacOS**: Ensure that you have the command line developer tools installed. You can install them by running `xcode-select --install` in the terminal.  

### **Windows**: Please follow the [Windows setup instructions.](##windows-setup)  


For the most part the package is fairly self-contained Python, however there are some utility functions which will automatically download the requisite Vega services for you. The full set of steps would then be:
  - Clone the repository to your local drive
  - Install the latest version of [Golang](https://go.dev)
  - Run `make` to automatically pull install dependencies
    - If you have your own instances of the various service to run from elsewhere, you can skip this step
  - Install the package into your local environment. 
    - The process for this will vary depending upon your package manager of choice. We provide here a full Poetry `pyproject.toml` and a `requirements.txt` which is derived from it. These are kept in sync through a check on all pull requests. You can [install Poetry here](https://python-poetry.org/docs/#installation) and get everything ready by running `poetry shell` and `poetry install` (or `poetry install --all-extras` to cover all optional extras too). 
 -  Run `make test` which checks all the python environment + vega imports are set up correctly, doesn't run Vega yet.
 -  Run `make test_integration` which checks that everything is set up correctly. Takes about 5 minutes.
 -  You're good now.

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

To run the example, start by running `poetry shell` if you're using poetry to activate the environment (If you're using another package manager, a similar command likely exists).  

 **_Ensure you are running these commands in your WSL terminal if using a Windows machine._**

Then, to run the example mentioned above call:
  `python -m examples.nullchain`

  If you've installed the console with `make ui` you can also extend this to visualise what is happening with the `--console` flag:

1. First you have to - Set the `run_with_console` flag to `True` when creating the `VegaServiceNull` class
2. Run the command

  ```
  python -m examples.nullchain --console
  ```
3. You should a message in the logs saying
`lynx: Can't access startfile http://localhost:*****/`
  
Open this link on your windows machine to see console.

Alternatively, to run a longer and more complex scenario, run:

  ```
  python -m vega_sim.scenario.adhoc -s historic_ideal_market_maker_v2 --pause
  ```

If you've installed the console with `make ui` you can also extend this to visualise what is happening with the `--console` flag:

  ```
  python -m vega_sim.scenario.adhoc -s historic_ideal_market_maker_v2 --pause --console
  ```



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


## Reinforcement Learning

The nascent framework for reinforcement learning applications of the Vega Market Sim can be found within `vega_sim.reinforcement`, this includes the beginnings of a 'background market' within the folder `vega_sim.reinforcement.full_market_sim`
alongside an agent in `vega_sim.reinforcement.learning_agent` which learns from a currently very simple set of inputs (alongside an input of a future price, to make learning on a random walk possible at all!) Usage is new, and the code strucure
and functionality is liable to change *significantly* in the future, however input is welcomed.

## Parameter Testing

One use of this framework is for testing the effect on Vega core itself of varying the various specified network and market parameters, allowing analysis and comparison and hopefully a more optimal set of parameters. 
To dig into this use case, the configuration for various existing tests lives in `vega_sim.parameter_test.parameter.configs` and these can be run by finding the parameter test name in that file and calling:

`python -m vega_sim.parameter_test.run -c YOUR_TEST_NAME_HERE`

This will run the configured scenario several times with each configured parameter value before outputting them into the `/parameter_results` folder in the root of the repository.

## Scenarios

To support the above mentioned parameter tests, and to allow for more complex capabilities, a set of scenarios (and agents who act within them) live in `vega_sim.scenario`. We aim here to provide a set of agent primitives which allow one to construct complex interactions and trading scenarios.

### Momentum Agent

One of the agents provided in the scenarios is momentum agent that can currently follow APO/ RSI/ STOCHRSI/ CMO/ MACD momentum strategies. A comprehensive scenario for momentum agent tests is in `vega_sim.scenario.comprehensive_market.scenario`, where mutileple momentum agents with different momentum strategies can be tested. 

To run momentum agents, you must first install the TA-Lib libraries. The instructions [here](https://github.com/mrjbq7/ta-lib#dependencies) are likely a good start. Follow this by running `poetry install -E agents`. Then, run `python examples.agent_market.MomentumAgent.py`, and the performance of momentum agents are shown in the notebook `examples.notebooks.MomentumAgentPerformance`. The agents can be configured in `ComprehensiveMarket`. For example, to run 2 momentum agents with APO and MACD strategies: 

```
ComprehensiveMarket(
  num_momentum_agents=2,
  momentum_trader_strategies=['APO', 'MACD'],
  momentum_trader_strategy_args=[
    {
      "fastperiod": 12,
      "slowperiod": 26,
    },
    {
      "fastperiod": 14,
      "slowperiod": 26,
      "signalperiod": 9,
    }
  ],  
)
```

## Release Process

Releases are aligned to Vega core [releases](https://github.com/vegaprotocol/vega/releases/), to provide a snapshot of working code for each release cutoff. To build and release a Vega Market Sim package, follow these steps:

 - Check [releases](https://github.com/vegaprotocol/vega/releases/) for the release tag you wish to target
 - Update `.env`'s `VEGA_SIM_VEGA_TAG` to reflect the last commit within that release
 - Update the `version` parameter in `pyproject.toml`. Poetry's `poetry version` command can help with this by automatically updating the file according to certain rules:
   - `poetry version patch`: `1.0.0` -> `1.0.1`
   - `poetry version minor`: `1.0.0` -> `1.1.0`
   - `poetry version major`: `1.0.0` -> `2.0.0`
 - Run `make` followed by a full integration test run
 - Create a branch containing these changes, then a pull request into `develop`
 - Use the GitHub [New Release](https://github.com/vegaprotocol/vega-market-sim/releases/new) dialog to create a release. Tag it with the version of Vega we are matching up to (e.g. `v0.62.5`) to trigger the deployment process.


## Windows Setup

## 1. Install [WSL]
To install Windows Subsystem for Linux (WSL) on Windows, follow these steps:

Note: The steps provided here are for Windows 10 version 2004 and later. If you have a different version of Windows, the steps might vary slightly.

1. Open the **Start** menu and search for "Turn Windows features on or off". Open the **Turn Windows features on or off** option from the search results.

2. In the **Windows Features** window that appears, scroll down and locate **Windows Subsystem for Linux**. Check the box next to it.

3. After checking the box, click **OK** and wait for Windows to apply the changes. Your computer might require a restart during this process.

4. Once your computer has restarted, open the Microsoft Store by searching for "Microsoft Store" in the Start menu.

5. In the Microsoft Store, search for the Linux distribution you want to install, such as Ubuntu, Debian, or OpenSUSE. Select the desired distribution from the search results.

6. Click the **Install** button to download and install the Linux distribution.

7. After the installation is complete, you can launch the Linux distribution from the Start menu or by searching for its name.

8. The first time you launch the Linux distribution, it will initialize and set up your Linux environment. This might take a few minutes.

9. Follow the on-screen prompts to create a username and password for your Linux environment.

Once the setup is complete, you will have a functioning Windows Subsystem for Linux (WSL) installation on your Windows system. You can open a Linux terminal and start using Linux commands and tools within the WSL environment.
  
## 2. Install 'Make' to your WSL
1. Open your terminal in Ubuntu.

2. Update the package lists for upgrades and new package installations by running the following command (You may be asked for your password here):

   ```
   sudo apt update
   ```

3. Once the package lists are updated, you can install `make` by running the following command:

   ```
   sudo apt install make
   ```

4. The package manager will ask for your confirmation to install the package. Type 'Y' and press Enter to proceed with the installation.

5. Ubuntu will download and install the `make` package along with any necessary dependencies.

6. Once the installation is complete, you can verify that `make` is installed by checking its version:

   ```
   make --version
   ```

   This command will display the version of `make` installed on your Ubuntu system.

## 3. Install 'Poetry' to your WSL
To install Poetry on Windows Subsystem for Linux (WSL), you can follow these steps:

1. Update the package lists and upgrade installed packages by running the following command:

    ```
    sudo apt update
    ```

2. Install the dependencies required for Poetry using the following command:

   ```
   sudo apt install python3-pip python3-venv
   ```

3. Once the dependencies are installed, you can proceed with the installation of Poetry. Use the following command to download and install Poetry:

   ```
   curl -sSL https://install.python-poetry.org | python3 -
   ```

4. After the installation is complete, you'll need to close and reopen your terminal or run the command `source $HOME/.poetry/env` to start using Poetry without restarting.

5. Verify the installation by running the following command:

   ```
   poetry --version
   ```

   This command will display the version of Poetry installed on your system.

## 4. Clone the Repository

1. Decide on the location where you want to create the new folder for the repository. For example, if you want to create it in your home directory, you can use the following command:

   ```
   cd ~
   ```

2. Create a new folder for the repository using the `mkdir` command followed by the desired folder name. For example, to create a folder named "vega-market-sim", use the following command:

   ```
   mkdir vega-market-sim
   ```

3. Navigate to the newly created folder using the `cd` command. For example:

   ```
   cd vega-market-sim
   ```

4. In your browser, open the repository's page "https://github.com/vegaprotocol/vega-market-sim".

5. Click on the green "Code" button and select the "HTTPS" option to copy the repository URL.

6. In your WSL terminal, use the `git clone` command followed by the repository URL you copied. The command should look like this:

   ```
   git clone https://github.com/vegaprotocol/vega-market-sim.git
   ```

## 5. Run make to automatically pull install dependencies 
1. Run the command:

    ```
    make
    ```
## 6. Install the package into your local environment. 
1. Run the command:
  
    ```
    poetry shell
    ```
2. Run the command:
 
     ```
    poetry install
    ```
   [OPTIONAL] 

    _To include all optional extras use:_
  
    ```
    poetry install --all-extras
    ```

## 7. Run initial tests
1. Run the command:
  
    ```
    make test
    ```

    This will check all the python environment + vega imports are set up correctly, doesn't run Vega yet.
## 8. Run integration tests
1. Run the command:
  
    ```
    make test_integration
    ```

    This will check that everything is set up correctly. Takes about 5 minutes. 
## 9. Set up Development environment
   ### 1. Install "Remote - WSL" extension
1. Launch Visual Studio Code on your Windows machine.

2. Open the Extensions view by clicking on the square icon on the left sidebar or by pressing `Ctrl+Shift+X`.

3. In the Extensions view, search for "Remote - WSL" in the search bar.

4. Look for the "Remote - WSL" extension in the search results. It should be the one published by Microsoft with the ID `ms-vscode-remote.remote-wsl`.

5. Click on the "Install" button next to the "Remote - WSL" extension.

6. Visual Studio Code will begin downloading and installing the extension.

7. Once the installation is complete, you will see an "Open" button instead of "Install". Click on the "Open" button to activate the extension.

8. Open your WSL terminal (ensure you are in the vega-market-sim directory). Run the command
   ```
   code .
   ```
This will open up a visual studio window connected to your linux environment.

__If visual studio is unable to connect to your environment perform these steps to restart your wsl__
1. Close Visual studio
2. Run **COMMAND PROMPT** as admin


    Find out which instance of WSL is running

      ```
      wsl -l --running
      ```

    Terminate all running instances of WSL

   ```
   wsl --shutdown
   ```

    Then simply restart WSL
   ```
   wsl 
   ```
3. Reopen Visual studio
4. Open your WSL terminal (ensure you are in the vega-market-sim directory). Run the command
   ```
   code .
   ```


## OPTIONAL Setup for the UI
## 1. Install Node to WSL
To install NVM (Node Version Manager) and Node.js version 16 in Windows Subsystem for Linux (WSL), follow these steps:

1. Install the required dependencies for NVM using the following command:

   ```
   sudo apt install curl ca-certificates bash
   ```

2. Download the NVM installation script using the following command:

   ```
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
   ```

3. Close and reopen your terminal or run the command `source ~/.bashrc` to load the NVM environment variables.

4. Verify that NVM is installed properly by running the following command:

   ```
   nvm --version
   ```

5. Install Node.js version 16 using NVM by running the following command:

   ```
   nvm install 16
   ```

   This command will download and install Node.js version 16 in your WSL environment.

6. Verify that Node.js is installed successfully by checking its version:

   ```
   node --version
   ```

   It should display the version number of Node.js 16.x.

7. To set Node.js 16 as the default version, run the following command:

   ```
   nvm alias default 16
   ```

   This will make Node.js version 16 the default version whenever you open a new terminal session.
## 2. Install Yarn
To install Yarn on Windows Subsystem for Linux (WSL), you can follow these steps:

1. Update the package lists and upgrade installed packages by running the following commands:

   ```
   sudo apt update
   ```

2. Install the necessary dependencies for Yarn using the following command:

   ```
   sudo apt install curl gnupg2
   ```

3. Import the Yarn repository's GPG key by running the following command:

   ```
   curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
   ```

4. Add the Yarn repository to the package manager's sources list by executing the following command:

   ```
   echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
   ```

5. Update the package lists again to include the Yarn repository:

   ```
   sudo apt update
   ```

6. Finally, install Yarn by running the following command:

   ```
   sudo apt install yarn
   ```

7. Verify that Yarn is installed by checking its version:

    ```
    yarn --version
    ```

## 3. Make UI
1.  Run the command:
  
    ```
    make ui
    ```


