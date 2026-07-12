"""Tests for NourishBot. Real CrewAI objects throughout; the only mock is the
final LLM kickoff (a live watsonx call), consistent with repo policy."""

import base64
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import nourishbot
from crewai import Agent, Crew, Process, Task


def test_no_hardcoded_credentials():
    source = Path(nourishbot.__file__).read_text()
    assert "os.environ" in source
    for marker in ("apikey=", "api_key=\"", "api_key='"):
        assert marker not in source.lower().replace(" ", "")


def test_encode_image_produces_valid_data_url(tmp_path):
    img = tmp_path / "meal.png"
    img.write_bytes(b"\x89PNG-fake-bytes")
    url = nourishbot.encode_image_to_data_url(str(img))
    assert url.startswith("data:image/png;base64,")
    assert base64.b64decode(url.split(",", 1)[1]) == b"\x89PNG-fake-bytes"


def test_encode_image_normalizes_jpg_to_jpeg(tmp_path):
    img = tmp_path / "meal.jpg"
    img.write_bytes(b"jpgdata")
    assert nourishbot.encode_image_to_data_url(str(img)).startswith("data:image/jpeg;base64,")


def test_agents_are_real_crewai_agents_with_roles():
    analyst, coach = nourishbot.build_agents()
    assert isinstance(analyst, Agent) and isinstance(coach, Agent)
    assert analyst.role == "Nutrition Analyst"
    assert coach.role == "Dietary Coach"
    assert analyst.multimodal is True


def test_tasks_wire_context_from_analysis_to_coaching():
    analyst, coach = nourishbot.build_agents()
    analyze_task, coach_task = nourishbot.build_tasks(analyst, coach)
    assert isinstance(analyze_task, Task) and isinstance(coach_task, Task)
    assert coach_task.context == [analyze_task]
    assert "{image_data_url}" in analyze_task.description
    assert "{user_goal}" in coach_task.description


def test_crew_is_sequential_with_both_agents_and_tasks():
    crew = nourishbot.build_crew()
    assert isinstance(crew, Crew)
    assert crew.process == Process.sequential
    assert len(crew.agents) == 2 and len(crew.tasks) == 2


def test_analyze_meal_passes_encoded_image_and_goal_to_kickoff(tmp_path):
    img = tmp_path / "meal.png"
    img.write_bytes(b"pixels")
    with patch.object(Crew, "kickoff", return_value="Great balance of protein!") as mock_kickoff:
        result = nourishbot.analyze_meal(str(img), "build muscle")
    assert result == "Great balance of protein!"
    inputs = mock_kickoff.call_args.kwargs["inputs"]
    assert inputs["user_goal"] == "build muscle"
    assert inputs["image_data_url"].startswith("data:image/png;base64,")


def test_llm_uses_watsonx_models_from_env_defaults():
    assert nourishbot.VISION_MODEL_ID.startswith("watsonx/")
    assert nourishbot.TEXT_MODEL_ID.startswith("watsonx/")
    llm = nourishbot.make_llm(nourishbot.TEXT_MODEL_ID)
    assert llm.model == nourishbot.TEXT_MODEL_ID
