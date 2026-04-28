from __future__ import annotations

from pydantic import BaseModel, Field, model_validator
from typing import Annotated

# cultural modifiers
UnitInterval = Annotated[float, Field(ge=0.0, le=1.0)]

class CulturalModifiers(BaseModel):
    """
    continuous [0,1] params derived from real national data
    modulate markov transition probabilities for culturally gated transitions

    sources: world values survey, oecd, world bank, bis, hofstede dimensions
    """
    # recovery and bankruptcy
    bankruptcy_stigma: UnitInterval = Field(
        description="Social and legal cost of personal bankruptcy - "
                    "High = terminal, low = transitory (0=US, 1=JP)"
    )
    social_safety_net: UnitInterval = Field(
        description="Strength of public welfare and unemployment systems. "
                    "(0=minimal, 1=Nordic)"
    )
 
    # institutional
    institutional_trust: UnitInterval = Field(
        description="Population trust in banks and government institutions. "
                    "Affects forbearance likelihood and sovereign default probability."
    )
    central_bank_independence: UnitInterval = Field(
        description="Degree of CB independence from government. "
                    "Low = government can force emergency easing."
    )
 
    # structural
    informality_index: UnitInterval = Field(
        description="Size and functional role of informal economy. "
                    "Governs informal sector absorption capacity."
    )
    ease_of_doing_business: UnitInterval = Field(
        description="Regulatory ease of firm creation and post-bankruptcy recovery."
    )
 
    # behavioural
    risk_tolerance: UnitInterval = Field(
        description="Cultural propensity for leverage and speculation."
    )
    collectivism: UnitInterval = Field(
        description="Preference for group outcomes over individual outcomes. "
                    "Affects household stress contagion dynamics."
    )

# initial state distribution - proportion of agents starting in each state (must sum = 1)
class HouseholdDistribution(BaseModel):
    thriving: UnitInterval = 0.10
    stable: UnitInterval = 0.55
    stressed: UnitInterval = 0.15
    speculative: UnitInterval = 0.08
    distressed: UnitInterval = 0.07
    defaulted: UnitInterval = 0.03
    bankrupt: UnitInterval = 0.01
    recovering: UnitInterval = 0.01
    informal: UnitInterval = 0.00
 
    @model_validator(mode="after")
    def must_sum_to_one(self) -> "HouseholdDistribution":
        total = sum(self.model_dump().values())
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"HouseholdDistribution must sum to 1.0, got {total:.6f}")
        return self
 
 
class FirmDistribution(BaseModel):
    expanding: UnitInterval = 0.10
    stable: UnitInterval = 0.55
    contracting: UnitInterval = 0.15
    distressed: UnitInterval = 0.08
    speculative: UnitInterval = 0.05
    zombie: UnitInterval = 0.03
    restructuring: UnitInterval = 0.02
    bankrupt: UnitInterval = 0.01
    dormant: UnitInterval = 0.01
 
    @model_validator(mode="after")
    def must_sum_to_one(self) -> "FirmDistribution":
        total = sum(self.model_dump().values())
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"FirmDistribution must sum to 1.0, got {total:.6f}")
        return self
 
 
class BankDistribution(BaseModel):
    healthy: UnitInterval = 0.40
    cautious: UnitInterval = 0.30
    constrained: UnitInterval = 0.15
    stressed: UnitInterval = 0.08
    forbearing: UnitInterval = 0.04
    illiquid: UnitInterval = 0.02
    insolvent: UnitInterval = 0.01
 
    @model_validator(mode="after")
    def must_sum_to_one(self) -> "BankDistribution":
        total = sum(self.model_dump().values())
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"BankDistribution must sum to 1.0, got {total:.6f}")
        return self
    
# population config - agent counts per type
class PopulationConfig(BaseModel):
    banks: Annotated[int, Field(ge=1, le=20)] = 8
    firms: Annotated[int, Field(ge=5, le=500)] = 100
    households: Annotated[int, Field(ge=1, le=20)] = 400
    investors: Annotated[int, Field(ge=1, le=20)] = 5
    # government, central_bank, informal are unitary (only one can exist)

class CountryProfile(BaseModel):
    id: str = Field(pattern=r"^[a-z0-9_]+$")
    name: str
    region: str
    modifiers: CulturalModifiers
    default_population: PopulationConfig = Field(default_factory=PopulationConfig)
    default_household_dist: HouseholdDistribution = Field(default_factory=HouseholdDistribution)
    default_firm_dist: FirmDistribution = Field(default_factory=FirmDistribution)
    default_bank_dist: BankDistribution = Field(default_factory=BankDistribution)
    notes: str = ""

# scenario config - loaded from configs/scenarios/<id>.yaml
class ParameterOverrides(BaseModel):
    """
    scenario-specific adjustments layered on top of country defaults
    all fields optional - only override what scenario requests
    """
    household_dist: HouseholdDistribution | None = None
    firm_dist: FirmDistribution | None = None
    bank_dist: BankDistribution | None = None

    # scalar modifiers - multipliers applied to base transition probs
    household_leverage_modifier: Annotated[float, Field(ge=0.0, le=5.0)] = 1.0
    credit_availability: UnitInterval = 1.0
    oil_shock_intensity: UnitInterval = 0.0
    fiscal_stimulus_intensity: UnitInterval = 0.0
    external_demand_shock: Annotated[float, Field(ge=-1.0, le=1.0)] = 0.0

class ScenarioConfig(BaseModel):
    id: str = Field(pattern=r"^[a-z0-9_]+$")
    name: str
    description: str
    tags: list[str] = Field(default_factory=list)
    country_profile_id: str
    parameter_override: ParameterOverrides = Field(default_factory=ParameterOverrides)
    llm_prompt = ""

# SimConfig - fully resolved configuration forf a single sim run
class SimConfig(BaseModel):
    scenario: ScenarioConfig
    country: CountryProfile
    population: PopulationConfig
    household_dist: HouseholdDistribution
    firm_dist: FirmDistribution
    bank_dist: BankDistribution
    neighborhood_k: Annotated[int, Field(ge=2, le=20)] = 8
    tick_rate_ms: Annotated[int, Field(ge=50, le=5000)] = 200
    random_seed: int | None = None