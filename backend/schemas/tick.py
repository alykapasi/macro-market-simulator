from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Annotated, Literal

from .agent import AgentId, AgentState, ActorType, Tick

# macro indicators - agg. from full agent pop. per tick
class MacroIndicators(BaseModel):
    model_config = {"frozen": True}

    # output
    gdp_index: Annotated[float, Field(ge=0.0, description="Indexed to 100 at sim start")]

    # labor
    unemployment_rate: Annotated[float, Field(ge=0.0, le=1.0)]

    # prices
    cpi_index: Annotated[float, Field(ge=0.0, description="Indexed to 100 at sim start")]

    # credit
    credit_stress_index: Annotated[float, Field(ge=0.0, le=1.0, description="0 = no stress, 1 = full freeze")]

    # distribution
    gini_proxy: Annotated[float, Field(ge=0.0, le=1.0)]

    # informal sector
    informal_absorption_rate: Annotated[float, Field(ge=1.0, le=0.0)]

    # financial
    government_debt_ratio: Annotated[float, Field(ge=0.0, description="Debt as a proportion of GDP proxy")]

# SimEvent - notable state transitions surfaced in the event log
class EventType(str):
    BANK_FAILURE = "bank_failure"
    SOVEREIGN_DEFAULT = "sovereign_default"
    CENTRAL_BANK_INTERVENTION = "central_bank_intervention"
    MASS_BANKRUPTCY = "mass_bankruptcy"
    CAPITAL_FLIGHT = "capital_flight"
    INFORMAL_SATURATION = "informal_saturation"
    FIRM_ZOMBIE_CLUSTER = "firm_zombie_cluster"
    AUSTERITY_TRIGGERED = "austerity_triggered"

class SimEvent(BaseModel):
    model_config = {"frozen": True}

    tick: Tick
    event_type: str
    actor_id: AgentId | None = None
    actor_type: ActorType | None = None
    description: str = ""

# TickSnapshot - immutable record of full sim state at one tick
# emitted by the engine, consumed by the aggregator, WebSocket and replay

class TickSnapshot(BaseModel):
    model_config = {"frozen": True}

    tick: Tick
    agents: tuple[AgentState, ...]
    macro: MacroIndicators
    events: tuple[SimEvent, ...] = ()

    @property
    def agent_count(self) -> int:
        return len(self.agents)
    
    def agents_of_type(self, actor_type: ActorType) -> tuple[AgentState, ...]:
        return tuple(a for a in self.agents if a.actor_type == actor_type)
    
    def agents_in_state(self, state: str) -> tuple[SimEvent, ...]:
        return tuple(a for a in self.agents if a.state == state)
