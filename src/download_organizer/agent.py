"""Agent definition for the Download Organizer."""

# Imports moved to function to optimize startup

SYSTEM_PROMPT = """Eres el 'Organizador de Descargas Inteligente'.
Tu objetivo es organizar los archivos descargados por el usuario en los directorios más apropiados.

REGLAS:
1.  Analiza el nombre del archivo y su tipo de contenido.
2.  Si el usuario proporciona instrucciones específicas (ej: 'mueve a proyectos'), SÍGUELAS.
    - Comprueba los directorios disponibles para ver si ya existe el directorio indicado por el usuario.
    - Si el directorio no existe, créalo.
    - Si el usuario no indica que muevas el archivo, manten la ubicación original.
3.  Si no hay instrucciones, infiere la mejor categoría (Documentos, Imágenes, Instaladores, etc.).
4.  Si el archivo es un comprimido (.zip, etc) y el usuario pide extraerlo, usa la herramienta de extracción.
5.  Verifica siempre las rutas de los archivos. Las descargas están en '~/Descargas'.
6.  Si el usuario pide borrar/eliminar, usa la herramienta delete_file y confirma la acción.
7.  Si el usuario pide renombrar un archivo, usa la herramienta rename_file y confirma la acción.
8.  Si el usuario pide crear un directorio, usa la herramienta create_directory y confirma la acción.
9.  NUNCA respondas con preguntas. Usa siempre una respuesta corta y directa.
10. No utilices emojis y responde únicamente: "Archivo guardado en [ruta]".
"""

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
    
    # Configuration
    config = AgentConfig(
        name="OrganizerAgent",
        provider=LLM_PROVIDER,
        model_name=LLM_MODEL,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.0,
    )
    
    # Memory (Short term is fine for this task)
    memory_service = MemoryService(store=InMemoryStore())
    address = MemoryAddress(conversation_id=conversation_id, agent_id="organizer")
    
    agent = BaseAgent(
        config=config,
        memory=memory_service,
        memory_address=address,
        tools=tools
    )
    
    return agent
