"""NourishBot — CrewAI meal-analysis assistant with Llama 4 vision.

A two-agent CrewAI pipeline: a vision-capable Nutrition Analyst extracts the
foods visible in a meal photo, and a Dietary Coach turns the analysis into
practical guidance. Wrapped in a small Gradio UI.

Credentials via environment variables only:
    WATSONX_APIKEY, WATSONX_URL (default us-south), WATSONX_PROJECT_ID
"""

import base64
import os
from pathlib import Path

from crewai import Agent, Crew, Process, Task
from crewai.llm import LLM

WATSONX_URL = os.environ.get("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
VISION_MODEL_ID = os.environ.get(
    "NOURISHBOT_VISION_MODEL", "watsonx/meta-llama/llama-4-maverick-17b-128e-instruct-fp8"
)
TEXT_MODEL_ID = os.environ.get("NOURISHBOT_TEXT_MODEL", "watsonx/ibm/granite-3-3-8b-instruct")


def encode_image_to_data_url(image_path: str) -> str:
    """Read an image file and return a base64 data URL for vision prompts."""
    path = Path(image_path)
    suffix = path.suffix.lower().lstrip(".") or "png"
    if suffix == "jpg":
        suffix = "jpeg"
    payload = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:image/{suffix};base64,{payload}"


def make_llm(model_id: str) -> LLM:
    """Build a CrewAI LLM handle pointed at watsonx.ai (credentials from env)."""
    return LLM(
        model=model_id,
        base_url=WATSONX_URL,
        api_key=os.environ.get("WATSONX_APIKEY"),
        temperature=0.2,
    )


def build_agents() -> tuple[Agent, Agent]:
    """Define the two NourishBot agents."""
    nutrition_analyst = Agent(
        role="Nutrition Analyst",
        goal=(
            "Identify every food item visible in a meal photo and estimate "
            "portion sizes, calories, and macronutrients."
        ),
        backstory=(
            "A registered dietitian with a decade of experience in visual "
            "food-diary assessment, known for precise, non-judgmental analysis."
        ),
        llm=make_llm(VISION_MODEL_ID),
        multimodal=True,
        verbose=False,
        allow_delegation=False,
    )
    dietary_coach = Agent(
        role="Dietary Coach",
        goal=(
            "Translate a nutrition analysis into two or three practical, "
            "encouraging suggestions tailored to the user's stated goal."
        ),
        backstory=(
            "A supportive health coach who focuses on realistic, sustainable "
            "changes rather than restrictive rules."
        ),
        llm=make_llm(TEXT_MODEL_ID),
        verbose=False,
        allow_delegation=False,
    )
    return nutrition_analyst, dietary_coach


def build_tasks(nutrition_analyst: Agent, dietary_coach: Agent) -> tuple[Task, Task]:
    """Define the analyse-then-coach task pair."""
    analyze_task = Task(
        description=(
            "Analyze the meal photo provided at {image_data_url}. List each "
            "visible food item with an estimated portion size, then estimate "
            "total calories, protein, carbohydrates, and fat."
        ),
        expected_output=(
            "A bullet list of identified foods with portions, followed by a "
            "one-line macro summary (kcal / protein / carbs / fat)."
        ),
        agent=nutrition_analyst,
    )
    coach_task = Task(
        description=(
            "Using the nutrition analysis, give the user two or three concrete "
            "suggestions aligned with their goal: {user_goal}."
        ),
        expected_output="Two to three numbered, actionable suggestions in a warm tone.",
        agent=dietary_coach,
        context=[analyze_task],
    )
    return analyze_task, coach_task


def build_crew() -> Crew:
    """Assemble the sequential two-agent crew."""
    analyst, coach = build_agents()
    analyze_task, coach_task = build_tasks(analyst, coach)
    return Crew(
        agents=[analyst, coach],
        tasks=[analyze_task, coach_task],
        process=Process.sequential,
        verbose=False,
    )


def analyze_meal(image_path: str, user_goal: str) -> str:
    """End-to-end entry point: photo + goal in, coaching text out."""
    crew = build_crew()
    result = crew.kickoff(
        inputs={
            "image_data_url": encode_image_to_data_url(image_path),
            "user_goal": user_goal,
        }
    )
    return str(result)


def build_ui():
    """Gradio interface (imported lazily so tests do not require gradio)."""
    import gradio as gr

    with gr.Blocks(title="NourishBot") as demo:
        gr.Markdown("# NourishBot\nUpload a meal photo and get nutrition coaching.")
        image_input = gr.Image(type="filepath", label="Meal photo")
        goal_input = gr.Textbox(label="Your goal", placeholder="e.g. cut calories, build muscle")
        output = gr.Textbox(label="NourishBot says", lines=10)
        submit = gr.Button("Analyze my meal")
        submit.click(analyze_meal, inputs=[image_input, goal_input], outputs=output)
    return demo


if __name__ == "__main__":
    build_ui().launch()
