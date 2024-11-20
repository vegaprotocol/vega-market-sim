from abc import abstractmethod
from collections import defaultdict, namedtuple
from typing import Dict, Optional, Tuple


from vega_sim.environment import VegaState
from vega_sim.environment.agent import Agent
from vega_sim.null_service import VegaServiceNull


from vega_sim.reinforcement.v2.states import State
from vega_sim.reinforcement.v2.agents.puppets import Action

WalletConfig = namedtuple("WalletConfig", ["name", "passphrase"])

# Send selling/buying MOs to hit LP orders
WALLET = WalletConfig("learner", "learner")


def state_fn(
    service: VegaServiceNull,
    agents: Dict[str, Agent],
    state_values=None,
) -> Tuple[State, Action]:
    learner = agents["learner"]
    return (learner.latest_state, learner.latest_action)


class LearningAgent:
    @abstractmethod
    def learning_step(self, results_dir: Optional[str] = None):
        pass

    @abstractmethod
    def update_memory(self, state: State, action: Action, reward: float):
        """
        Updates memory of the agent
        """
        pass

    def clear_memory(self):
        pass

    @abstractmethod
    def step(self, state: State) -> Action:
        pass

    @abstractmethod
    def save(self, results_dir: str):
        pass

    @abstractmethod
    def load(self, results_dir: str):
        pass


class TorchLearningAgent(LearningAgent):
    @abstractmethod
    def __init__(
        self,
        device: str,
        logfile_pol_imp: str,
        logfile_pol_eval: str,
        logfile_pnl: str,
        discount_factor: float,
        inventory_penalty: float = 0.0,
    ):
        super().__init__()

        self.step_num = 0
        self.latest_state = None
        self.latest_action = None
        self.device = device
        self.discount_factor = discount_factor

        self.memory = defaultdict(list)
        self.memory_capacity = 100_000

        # Coefficients for regularisation
        self.coefH_discr = 1.0
        self.coefH_cont = 0.01
        # losses logger
        self.losses = defaultdict(list)
        # logfile
        self.logfile_pol_imp = logfile_pol_imp
        self.logfile_pol_eval = logfile_pol_eval
        self.logfile_pnl = logfile_pnl

        self.learningIteration = 0

    @abstractmethod
    def move_to_device(self):
        pass

    @abstractmethod
    def move_to_cpu(self):
        pass

    @abstractmethod
    def learning_step(self, results_dir: Optional[str] = None):
        pass

    def _update_memory(
        self,
        state: State,
        action: Action,
        reward: float,
    ):
        pass

    def update_memory(self, state: State, action: Action, reward: float):
        """
        Updates memory of the agent, and removes old tuples (s,a,r,s) if memory exceeds its capacity
        """
        self._update_memory(state, action, reward)
        # remove old tuples if memory exceeds its capaciy
        for key in self.memory.keys():
            if len(self.memory[key]) > self.memory_capacity:
                first_n = len(self.memory[key]) - self.memory_capacity
                del self.memory[key][:first_n]
        return 0

    def clear_memory(self):
        for key in self.memory.keys():
            self.memory[key].clear()

    @abstractmethod
    def create_dataloader(self, batch_size):
        """
        creates dataset and dataloader for training.
        """
        pass

    @abstractmethod
    def empty_action(self) -> Action:
        pass

    @abstractmethod
    def step(self, vega_state: VegaState):
        pass

    @abstractmethod
    def save(self, results_dir: str):
        pass

    @abstractmethod
    def load(self, results_dir: str):
        pass
