from typing import Literal, Mapping
from .poker_agent import PokerAgent
from .calling_agent import CallingAgent
from .simple_agent import SimpleAgent

AgentType = Literal["calling", "maniac", "nit", "simple"]


AgentType2Agent: Mapping[AgentType, PokerAgent] = {
    "calling": CallingAgent(),
    "simple": SimpleAgent(),
}


def build_action_agent(type: AgentType):
    assert type in AgentType2Agent, AgentType2Agent.keys()
    return AgentType2Agent[type]
