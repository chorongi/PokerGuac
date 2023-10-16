from typing import Literal, Mapping, Tuple
from .poker_agent import PokerAgent
from .calling_agent import CallingAgent
from .simple_agent import SimpleAgent
from .all_in_agent import AllInAgent


# ALL_AGENT_TYPES = ["calling", "maniac", "nit", "simple", "all_in"]
ALL_AGENT_TYPES = ["calling", "all_in"]
# ALL_AGENT_TYPES = ["all_in"]
AgentType = Literal[tuple(ALL_AGENT_TYPES)]  # type: ignore


AgentType2Agent: Mapping[AgentType, PokerAgent] = {
    "calling": CallingAgent(),
    "simple": SimpleAgent(),
    "all_in": AllInAgent(),
}


def build_action_agent(type: AgentType):
    assert type in AgentType2Agent, AgentType2Agent.keys()
    return AgentType2Agent[type]
