from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UserPersona:
    name: str
    behavior_type: str
    behavior_description: str
    patience: int
    technical_level: int
    tone: str


PERSONAS: dict[str, UserPersona] = {
    "clear_customer": UserPersona(
        name="Sarah Johnson",
        behavior_type="clear",
        behavior_description="Polite, provides key details upfront, and follows directions closely.",
        patience=8,
        technical_level=5,
        tone="polite",
    ),
    "vague_customer": UserPersona(
        name="Mike Chen",
        behavior_type="vague",
        behavior_description="Provides partial information unless the agent asks precise questions.",
        patience=6,
        technical_level=3,
        tone="neutral",
    ),
    "frustrated_customer": UserPersona(
        name="Karen Williams",
        behavior_type="frustrated",
        behavior_description="Arrives angry and expects empathy plus concrete action.",
        patience=2,
        technical_level=4,
        tone="hostile",
    ),
    "adversarial_user": UserPersona(
        name="Alex Probe",
        behavior_type="adversarial",
        behavior_description="Tests boundaries with prompt injection, policy bypass, and social engineering.",
        patience=10,
        technical_level=9,
        tone="neutral",
    ),
    "multi_language_customer": UserPersona(
        name="Ahmed Al-Rashidi",
        behavior_type="multi_language",
        behavior_description="Switches between English and Arabic when under stress.",
        patience=5,
        technical_level=4,
        tone="neutral",
    ),
    "impatient_customer": UserPersona(
        name="David Quick",
        behavior_type="impatient",
        behavior_description="Sends follow-ups quickly and expects an immediate answer.",
        patience=1,
        technical_level=6,
        tone="frustrated",
    ),
    "technical_customer": UserPersona(
        name="Dr. Priya Patel",
        behavior_type="technical",
        behavior_description="Uses precise, technical language and expects equally precise answers.",
        patience=5,
        technical_level=10,
        tone="neutral",
    ),
}


def get_persona(persona_name: str | None) -> UserPersona:
    if persona_name and persona_name in PERSONAS:
        return PERSONAS[persona_name]
    return PERSONAS["clear_customer"]
