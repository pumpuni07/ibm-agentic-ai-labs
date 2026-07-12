"""Tests for the AG2 healthcare GroupChat. Real AG2 agents and GroupChat
machinery; only live LLM completions are avoided (repo policy)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import healthcare_chat


@pytest.fixture(autouse=True)
def _placeholder_api_key(monkeypatch):
    """AG2 constructs an OpenAI client eagerly at agent creation; provide a
    placeholder key so tests never depend on ambient environment state.
    No live API calls are made anywhere in this suite."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-placeholder-key")
from autogen import AssistantAgent, GroupChat, GroupChatManager, UserProxyAgent


def test_agents_have_expected_roles_and_disclaimer():
    patient, specialists = healthcare_chat.build_agents()
    assert isinstance(patient, UserProxyAgent)
    names = [a.name for a in specialists]
    assert names == ["TriageNurse", "GeneralPractitioner", "WellnessAdvisor"]
    for agent in specialists:
        assert isinstance(agent, AssistantAgent)
        assert "not a medical professional" in agent.system_message


def test_group_chat_is_round_robin_with_four_agents():
    groupchat, manager = healthcare_chat.build_group_chat(max_round=6)
    assert isinstance(groupchat, GroupChat) and isinstance(manager, GroupChatManager)
    assert len(groupchat.agents) == 4
    assert groupchat.max_round == 6
    assert groupchat.speaker_selection_method == "round_robin"


def test_round_robin_speaker_order_cycles_through_specialists():
    groupchat, _ = healthcare_chat.build_group_chat()
    patient = groupchat.agents[0]
    first = groupchat.next_agent(patient, groupchat.agents)
    second = groupchat.next_agent(first, groupchat.agents)
    third = groupchat.next_agent(second, groupchat.agents)
    assert [first.name, second.name, third.name] == [
        "TriageNurse",
        "GeneralPractitioner",
        "WellnessAdvisor",
    ]


def test_credentials_come_from_environment_only(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-from-env")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.test/v1")
    config = healthcare_chat.make_llm_config()
    entry = config["config_list"][0]
    assert entry["api_key"] == "test-key-from-env"
    assert entry["base_url"] == "https://example.test/v1"
    source = Path(healthcare_chat.__file__).read_text()
    assert "sk-" not in source
