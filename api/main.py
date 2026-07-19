from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent.brain import run_turn, execute_approved_action
from agent.approval import approval_queue
import agent.osint.recon  # noqa: F401

app = FastAPI(title="Agentic AI Companion")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your actual frontend origin before going to production
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    tenant_id: str
    message: str
    model: str = "claude"  # see agent/providers/registry.py for aliases: claude, gpt4o, gemini, llama, deepseek, grok


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    reply = run_turn(tenant_id=req.tenant_id, user_message=req.message, model_alias=req.model)
    return ChatResponse(reply=reply)


@app.get("/approvals/{tenant_id}")
def list_pending_approvals(tenant_id: str):
    pending = approval_queue.list_pending(tenant_id)
    return [
        {"id": a.id, "tool_name": a.tool_name, "tool_input": a.tool_input, "created_at": str(a.created_at)}
        for a in pending
    ]


class ApprovalDecision(BaseModel):
    tenant_id: str
    approve: bool


@app.post("/approvals/{action_id}/decide")
def decide_approval(action_id: str, decision: ApprovalDecision):
    action = approval_queue.decide(action_id, decision.approve)
    if not action:
        raise HTTPException(status_code=404, detail="Approval request not found")
    if not decision.approve:
        return {"status": "rejected", "id": action_id}
    result = execute_approved_action(decision.tenant_id, action_id)
    return {"status": "executed", "id": action_id, "result": result}


@app.get("/health")
def health():
    return {"status": "ok"}
