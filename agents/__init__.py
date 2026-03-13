"""agents — Módulo de agentes institucionales.

Siete tipos de agentes:
    JudgeAgent, LegislatorAgent, UnionAgent,
    RegulatedFirmAgent, CitizenAgent, RegulatorAgent
"""
from agents.base import BaseLegalAgent
from agents.judge import JudgeAgent
from agents.legislator import LegislatorAgent
from agents.union import UnionAgent
from agents.firm import RegulatedFirmAgent
from agents.citizen import CitizenAgent
from agents.regulator import RegulatorAgent

__all__ = [
    "BaseLegalAgent",
    "JudgeAgent",
    "LegislatorAgent",
    "UnionAgent",
    "RegulatedFirmAgent",
    "CitizenAgent",
    "RegulatorAgent",
]
