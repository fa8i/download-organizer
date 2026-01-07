# Smart Download Organizer

This project is a smart download manager powered by AI agents ([**agentify**](https://github.com/fa8i/Agentify)). Its goal is to automatically categorize and organize the files you download.

> [!NOTE]
> This software is designed specifically for **Linux** environments (tested on Ubuntu with X11). It uses `systemd` for service management and GTK4 for the graphical interface.

![Smart Download Organizer Demo](assets/pic_demo.png)

## Functionality

The system runs as a background *daemon* monitoring your `~/Downloads` folder. When it detects a new file:

1.  **Intercepts the download**: Detects the new file and waits for it to finish writing.
2.  **Requests Action**: Shows a popup dialog asking what to do. Options:
    *   **Confirm (Enter)**: If you type an instruction, the AI Agent will process it.
    *   **Auto-classify (Timeout/Empty)**: If you don't respond within 45 seconds or press Enter without text, it organizes the file automatically based on its extension.
    *   **Cancel (Esc)**: Ignores the file and leaves it where it is.

### Auto-Classification
If no instructions are given, files are automatically moved to:
*   `Pictures`: .jpg, .png, .webp, ...
*   `Documents`: .pdf, .docx, .txt, ...
*   `Videos`: .mp4, .mkv, ...
*   `Music`: .mp3, .flac, ...
*   `Archives`: .zip, .rar, ...
*   `Code`: .py, .js, ...

### Smart Agent (AI)
If you write an instruction in the dialog (e.g., *"Move to invoices folder and rename to Invoice_January"*), the agent:
*   Analyzes your request with a **fully configurable LLM**.
    *   Compatible with **OpenAI**, **DeepSeek**, **Anthropic (Claude)**, **Google Gemini**, and more (via [agentify](https://github.com/fa8i/Agentify)).
*   Can create folders, rename files, and move them to any subdirectory in your home folder.
*   Can extract archive files if requested.
*   Can **delete** files if you instruct it to (e.g., *"Delete this file"*).

## Installation and Auto-start

To ensure the organizer starts automatically with your system:

1.  Copy the service file `download-organizer.service` to `~/.config/systemd/user/`.
    *(Create the directory if it doesn't exist)*.

2.  Enable and start the service:
    ```bash
    systemctl --user enable --now download-organizer
    ```
3. En caso de actualizar el código, reinicia el servicio:
    ```bash
    systemctl --user restart download-organizer
    ```

## Configuration

Configuration settings can be found in `src/download_organizer/config.py`.

### Customization
You can fully customize the behavior:
*   **Folder Names**: Modify `config.py` to change the destination folders (e.g., change "Pictures" to "Fotos" or "Assets").
*   **Agent Prompts**: Edit `src/download_organizer/agent.py` to change the `SYSTEM_PROMPT`. You can translate it to any language or give the agent a specific personality.
*   **UI Messages**: Open `src/download_organizer/ui/window.py` to modify the popup labels, button text, or placeholder messages to your preferred language.

