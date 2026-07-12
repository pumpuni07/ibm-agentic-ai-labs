"""Step 1 — Prompt templating with a minimal template class."""
from core import SimplePromptTemplate

def main():
    template = SimplePromptTemplate("Summarize {topic} for a {audience} audience. Topic again: {topic}.")
    print(template.render(topic="tropical ecology", audience="general"))

if __name__ == "__main__":
    main()
