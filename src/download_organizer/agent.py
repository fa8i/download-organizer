"""Agent definition for the Download Organizer."""

from .prompts import SYSTEM_PROMPT

def create_organizer_agent(conversation_id: str = "organizer_session"):
    """Creates and returns the organizer agent."""
    
    # Lazy imports to optimize startup
    from agentify.core.agent import BaseAgent
    from agentify.core.config import AgentConfig
    from agentify.memory.service import MemoryService
    from agentify.memory.stores.in_memory_store import InMemoryStore
    from agentify.memory.interfaces import MemoryAddress

    from .config import LLM_PROVIDER, LLM_MODEL
    from .tools.filesystem import move_file, create_directory, rename_file, list_home_directories, get_file_info, delete_file
    from .tools.extractor import can_extract, extract_archive
    
    # Tools list
    tools = [
        move_file,
        create_directory,
        rename_file,
        list_home_directories,
        get_file_info,
        can_extract,
        extract_archive,
        delete_file
    ]
    
    config = AgentConfig(
        name="OrganizerAgent",
        provider=LLM_PROVIDER,
        model_name=LLM_MODEL,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.0,
    )
    
    memory_service = MemoryService(store=InMemoryStore())
    address = MemoryAddress(conversation_id=conversation_id, agent_id="organizer")
    
    agent = BaseAgent(
        config=config,
        memory=memory_service,
        memory_address=address,
        tools=tools
    )
    
    return agent
