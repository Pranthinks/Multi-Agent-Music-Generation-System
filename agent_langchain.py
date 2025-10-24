"""
LangChain Multi-Agent System
Main entry point that coordinates all agents and tools
"""
from agents.multi_agent_system import LangChainMultiAgentSystem
from utils.database import load_database, save_database


def create_langchain_multiagent_system(api_key: str):
    """Factory function to create the multi-agent system"""
    return LangChainMultiAgentSystem(api_key)


__all__ = [
    'create_langchain_multiagent_system',
    'LangChainMultiAgentSystem',
    'load_database',
    'save_database'
]