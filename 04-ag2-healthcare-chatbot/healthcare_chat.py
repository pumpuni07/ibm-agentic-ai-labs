"""AG2 (AutoGen) Healthcare Chatbot — multi-agent GroupChat triage.

Three specialist agents collaborate in a round-robin GroupChat to handle a
patient inquiry: a Triage Nurse gathers symptoms, a General Practitioner
gives non-diagnostic guidance, and a Wellness Advisor adds lifestyle advice.
A user proxy represents the patient. Educational demo only — not medical advice.

Credentials via environment variables only: OPENAI_API_KEY (or a
watsonx-compatible endpoint via OPENAI_BASE_URL).
"""

import os

from autogen import AssistantAgent, GroupChat, GroupChatManager, UserProxyAgent

MODEL_ID = os.environ.get("HEALTHCARE_MODEL", "gpt-4o-mini")

DISCLAIMER = (
    "I am an educational assistant, not a medical professional. "
    "For diagnosis or treatment, please consult a licensed clinician."
)


def make_llm_config() -> dict:
    """LLM config for all agents; API key strictly from the environment."""
    config = {"model": MODEL_ID, "api_key": os.environ.get("OPENAI_API_KEY")}
    base_url = os.environ.get("OPENAI_BASE_URL")
    if base_url:
        config["base_url"] = base_url
    return {"config_list": [config], "temperature": 0.3}


def build_agents() -> tuple[UserProxyAgent, list[AssistantAgent]]:
    """Create the patient proxy and the three specialist agents."""
    llm_config = make_llm_config()

    patient = UserProxyAgent(
        name="Patient",
        human_input_mode="NEVER",
        code_execution_config=False,
        max_consecutive_auto_reply=0,
    )
    triage_nurse = AssistantAgent(
        name="TriageNurse",
        system_message=(
            "You are a triage nurse. Ask focused follow-up questions to "
            "clarify symptoms, duration, and severity. Flag any red-flag "
            "symptoms that need urgent in-person care. " + DISCLAIMER
        ),
        llm_config=llm_config,
    )
    general_practitioner = AssistantAgent(
        name="GeneralPractitioner",
        system_message=(
            "You are a general practitioner providing general, non-diagnostic "
            "health information based on the triage summary. Never diagnose; "
            "explain common causes and when to seek care. " + DISCLAIMER
        ),
        llm_config=llm_config,
    )
    wellness_advisor = AssistantAgent(
        name="WellnessAdvisor",
        system_message=(
            "You are a wellness advisor. Offer practical lifestyle, rest, "
            "hydration, and self-care suggestions consistent with the GP's "
            "guidance. " + DISCLAIMER
        ),
        llm_config=llm_config,
    )
    return patient, [triage_nurse, general_practitioner, wellness_advisor]


def build_group_chat(max_round: int = 6) -> tuple[GroupChat, GroupChatManager]:
    """Assemble the round-robin GroupChat and its manager."""
    patient, specialists = build_agents()
    groupchat = GroupChat(
        agents=[patient, *specialists],
        messages=[],
        max_round=max_round,
        speaker_selection_method="round_robin",
    )
    manager = GroupChatManager(groupchat=groupchat, llm_config=make_llm_config())
    return groupchat, manager


def run_consultation(patient_message: str, max_round: int = 6):
    """Run one consultation round-trip and return the chat result."""
    groupchat, manager = build_group_chat(max_round=max_round)
    patient = groupchat.agents[0]
    return patient.initiate_chat(manager, message=patient_message)


if __name__ == "__main__":
    print(run_consultation("I have had a mild headache and fatigue for two days."))
