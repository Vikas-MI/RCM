from pydantic import BaseModel, Field


class PolicyAskIn(BaseModel):
    question: str = Field(min_length=3)
    top_k: int = Field(default=3, ge=1, le=8)


class PolicyCitation(BaseModel):
    id: str
    title: str
    policy_id: str
    category: str
    score: float
    snippet: str


class PolicyAskOut(BaseModel):
    answer: str
    citations: list[PolicyCitation]
    disclaimer: str
    mode: str
