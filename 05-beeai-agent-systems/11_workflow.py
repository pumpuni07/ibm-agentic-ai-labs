"""Step 11 — A two-step BeeAI Workflow with typed state."""
from pydantic import BaseModel
from beeai_framework.workflows import Workflow

class PipelineState(BaseModel):
    text: str
    word_count: int = 0
    shouted: str = ""

def count_words(state: PipelineState):
    state.word_count = len(state.text.split())
    return "shout"

def shout(state: PipelineState):
    state.shouted = state.text.upper()
    return Workflow.END

def build_workflow() -> Workflow:
    workflow = Workflow(schema=PipelineState)
    workflow.add_step("count", count_words)
    workflow.add_step("shout", shout)
    return workflow

if __name__ == "__main__":
    import asyncio
    async def main():
        run = await build_workflow().run(PipelineState(text="bee ai workflows are neat"))
        print(run.state.word_count, run.state.shouted)
    asyncio.run(main())
