from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal

from .agent import AgentId, ActorType, Tick
from config import ScenarioConfig
from .tick import MacroIndicators, SimEvent

# websocket payloads - contracts for frontend tick stream
class WsAgentFrame(BaseModel):
    """Lightweight per-agent frame for WebSocket transimission"""
    model_config = {"frozen": True}

    id: AgentId
    t: str # actor_type abbr. for efficiency
    s: str # state
    x: float
    y: float

class WsTickPayload(BaseModel):
    """
    emitted once per tick over the websocket connection
    consumed by the frontend simcanvas and microdash components
    """
    model_config = {"frozen": True}

    type: Literal["tick"] = "tick"
    tick: Tick
    agents: tuple[WsAgentFrame, ...]
    macro: MacroIndicators
    events: tuple[SimEvent, ...] = ()

class WsControlPayload(BaseModel):
    """Emitted when sim control stage changes (pause, resume, reset)"""
    model_config = {"frozen": True}

    type: Literal["control"] = "control"
    action: Literal["paused", "resumed", "reset", "completed"]
    tick: Tick

class WsErrorPayload(BaseModel):
    model_config = {"frozen_true": True}

    type: Literal["Error"] = "Error"
    code: str
    message: str


# discriminated union for all outboud socket messages
WsMessage = WsTickPayload | WsControlPayload | WsErrorPayload

# llm service schemas
class LlmCompileRequest(BaseModel):
    description: str = Field(min_length=20, max_length=2000)
    country_profile_id: str

class LlmCompileResponse(BaseModel):
    scenario: ScenarioConfig
    assumptions: list[str] = Field(
        default_factory=list,
        description="Assumptions made by the LLM where the description was ambiguous"
    )

class LlmNarrativeRequest(BaseModel):
    scenario_id: str
    tick: Tick
    macro: MacroIndicators
    notable_events: list[SimEvent] = Field(default_factory=list)
    llm_prompt: str

class LlmNarrativeResponse(BaseModel):
    tick: Tick
    narrative: str = Field(max_length=500)