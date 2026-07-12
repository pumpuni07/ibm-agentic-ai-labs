"""Step 2 — The same idea with BeeAI's real PromptTemplate."""
from pydantic import BaseModel
from beeai_framework.template import PromptTemplate, PromptTemplateInput

class SummaryInput(BaseModel):
    topic: str
    audience: str

def build_template() -> PromptTemplate:
    return PromptTemplate(
        PromptTemplateInput(
            schema=SummaryInput,
            template="Summarize {{topic}} for a {{audience}} audience.",
        )
    )

def main():
    print(build_template().render(topic="coral reefs", audience="policy"))

if __name__ == "__main__":
    main()
