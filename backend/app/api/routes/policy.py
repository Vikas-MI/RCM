from fastapi import APIRouter

from app.integrations.rag.cms_policies import CMS_POLICY_CHUNKS
from app.integrations.rag.policy_assistant import ask_policy
from app.schemas.policy import PolicyAskIn, PolicyAskOut

router = APIRouter(prefix="/policy", tags=["policy-rag"])


@router.get("/corpus")
def corpus():
    """List synthetic CMS policy chunks in the local vector store."""
    return {
        "chunks": [
            {
                "id": c["id"],
                "title": c["title"],
                "policy_id": c["policy_id"],
                "category": c["category"],
            }
            for c in CMS_POLICY_CHUNKS
        ],
        "eli5": (
            "These are pretend Medicare rule pages. RAG = find the best pages for your "
            "question, then answer using them."
        ),
        "disclaimer": "Synthetic policies only — not CMS.gov.",
    }


@router.post("/ask", response_model=PolicyAskOut)
def ask(body: PolicyAskIn):
    return ask_policy(body.question, top_k=body.top_k)
