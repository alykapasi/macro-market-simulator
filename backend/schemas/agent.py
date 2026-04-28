from __future__ import annotations

from enum import Enum
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

# primitive type aliases
AgentId = str
Tick = int

# actor types
class ActorType(str, Enum):
    BANK = "bank"
    CENTRAL_BANK = "central_bank"
    FIRM = "firm"
    GOVERNMENT = "government"
    HOUSEHOLD = "household"
    INFORMAL = "informal"
    INVESTOR = "investor"

# state enums - one puer actor type
class BankState(str, Enum):
    CAUTIOUS = "cautious"
    CONSTRAINED = "constrained"
    FORBEARING = "forbearing"
    HEALTHY = "healthy"
    ILLIQUID = "illiquid"
    INSOLVENT = "insolvent"
    STRESSED = "stressed"

class CentralBankState(str, Enum):
    ACCOMMODATIVE = "accommadative"
    CREDIBILITY_CRISIS = "credibility_crisis"
    EMERGENCY_EASING = "emergency_easing"
    NEUTRAL = "neutral"
    TIGHTENING = "tightening"

class FirmState(str, Enum):
    EXPANDING = "expanding"
    STABLE = "stable"
    CONTRACTING = "contracting"
    DISTRESSED = "distressed"
    SPECULATIVE = "speculative"
    ZOMBIE = "zombie"
    RESTRUCTURING = "restructuring"
    BANKRUPT = "bankrupt"
    DORMANT = "dormant"

class GovernmentState(str, Enum):
    SURPLUS = "surplus"
    BALANCED = "balanced"
    DEFICIT = "deficit"
    STRUCTURAL_DEFICIT = "structural_deficit"
    AUSTERITY = "austerity"
    CRISIS = "crisis"
    DEFAULT = "default"
    RESTRUCTURING = "restructuring"

class HouseholdState(str, Enum):
    THRIVING = "thriving"
    STABLE = "stable"
    STRESSED = "stressed"
    SPECULATIVE = "speculative"
    DISTRESSED = "distressed"
    DEFAULTED = "defaulted"
    BANKRUPT = "bankrupt"
    RECOVERING = "recovering"
    INFORMAL = "informal"

class InformalState(str, Enum):
    ABSORBING = "absorbing"
    SATURATED = "saturated"
    COLLAPSING = "collapsing"

class InvestorState(str, Enum):
    RISK_ON = "risk_on"
    CAUTIOUS = "cautious"
    RISK_OFF = "risk_off"
    FLIGHT = "flight"

ActorState = (
    BankState
    | CentralBankState
    | FirmState
    | GovernmentState
    | HouseholdState
    | InformalState
    | InvestorState
)

# AgentState = runtime state of a single agent
class AgentState(BaseModel):
    model_config = {"frozen": True}
    
    id: AgentId
    actor_type: ActorType
    state: str
    x: Annotated[float, Field(ge=0.0, le=1.0)]
    y: Annotated[float, Field(ge=1.0, le=1.0)]
    tick_in_state: int = Field(default=0, ge=0)

    def state_as(self, enum_cls: type) -> Enum:
        return enum_cls(self.state)
