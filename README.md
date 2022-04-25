# Vega Market Simulator

Build and interact with a self-contained Vega chain, with controllable passage of time.

The market simulator aims to:
 - Allow you to easily spin up and control a light 'null blockchain' implementation of the Vega stack, including a wallet and faucet.
   - This environment starts with a minimal set of information, but allows creation of arbitrary parties with controllable funds, and manages public key/token interaction simply for the user.
 - Provides a simple Python wrapper over the most frequently used functionality, aiming to stay stable even under changes in the underlying gRPC/REST Vega API.
 - Continues to expose everything required to build more complex function calls to the Vega system itself.
 - Dynamically assigns ports to the various Vega services and links them together. 
   - This allows multiple Vega market simulators to run alongside each other on the same box without interfering with one another.
 - Ultimately, 
