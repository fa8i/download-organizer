"""Main entry point for the Download Organizer Daemon."""

import sys
import time
import logging
import signal
from pathlib import Path

# Configure path so we can run as a module
# Configure path so we can run as a module
PKG_DIR = Path(__file__).parent.parent
if str(PKG_DIR) not in sys.path:
    sys.path.insert(0, str(PKG_DIR))

# LOAD ENVIRONMENT VARIABLES (API KEY)
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)


from download_organizer.monitor import run_monitor_loop
from download_organizer.notifier import show_download_dialog, DialogResult
from download_organizer.agent import create_organizer_agent
from download_organizer.config import DOWNLOADS_DIR, DATA_DIR
from download_organizer.categorizer import get_default_destination
from download_organizer.tools.filesystem import move_file

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("OrganizerNode")

def process_new_file(file_path: str):
    """Callback when a new file is detected."""
    filename = Path(file_path).name
    logger.info(f"📥 Detectado: {filename}")
    
    # 1. Get file size
    try:
        size = Path(file_path).stat().st_size
    except FileNotFoundError:
        logger.warning(f"File vanished: {file_path}")
        return

    # 2. Show UI
    logger.info("Waiting for user...")
    response = show_download_dialog(filename, size)
    
    logger.info(f"Dialog result: {response.result}")
    
    if response.result == DialogResult.CANCELLED:
        logger.info(f"⏭️  Skipped: {filename} (Users cancelled)")
        return

    # 3. Action
    if response.should_auto_classify:
        # Auto-organize
        dest_dir, category = get_default_destination(file_path)
        logger.info(f"🤖 Auto-organizing to: {category}")
        move_file(file_path, dest_dir)
        
    elif response.result == DialogResult.CONFIRMED and response.user_input:
        # Agent Instruction
        logger.info(f"🧠 Agent trigger: '{response.user_input}'")
        agent = create_organizer_agent()
        
        prompt = f"I have a file at '{file_path}'. The user wants: '{response.user_input}'. Organize it."
        
        try:
            result = agent.run(prompt)
            # handle generator response if needed, for now simple run
            if hasattr(result, "__iter__") and not isinstance(result, str):
                 out_text = "".join([str(chunk) for chunk in result])
                 logger.info(f"Agent: {out_text}")
            else:
                 logger.info(f"Agent: {result}")
                 
        except Exception as e:
            logger.error(f"Agent failed: {e}")

def main():
    print("==================================================")
    print("🚀 Smart Download Organizer (System Service)")
    print(f"📁 Watching: {DOWNLOADS_DIR}")
    print("==================================================")
    
    # Create data dir
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Run loop
    run_monitor_loop(process_new_file)

if __name__ == "__main__":
    main()
