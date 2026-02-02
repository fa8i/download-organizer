# 📂 Smart Download Organizer

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/platform-linux-black?style=for-the-badge&logo=linux)
![Memory Usage](https://img.shields.io/badge/memory-<50MB-green?style=for-the-badge&logo=ram)
![License](https://img.shields.io/badge/license-MIT-purple?style=for-the-badge)

**AI-powered assistant that keeps your `Downloads` folder organized.**  
Powered by [**Agentify**](https://github.com/fa8i/Agentify).

</div>

---

## 🚀 Overview

**Smart Download Organizer** runs silently in the background, monitoring your downloads. When a new file arrives, it uses **[Agentify](https://github.com/fa8i/Agentify)** to understand your instructions and organize files automatically.

> [!NOTE]
> **Linux Only**: Designed for **Linux** (tested on Ubuntu/X11).

![Smart Download Organizer Demo](assets/pic_demo.png)

## ✨ Key Features

*   **🤖 AI-Powered**: If you write an instruction in the dialog (e.g., *"Move to invoices folder and rename to Invoice_January"*), the agent:
    *   Analyzes your request with a **fully configurable LLM**.
    *   Compatible with **OpenAI**, **DeepSeek**, **Anthropic (Claude)**, **Google Gemini**, and more (via [Agentify](https://github.com/fa8i/Agentify)).
    *   Can create folders, rename files, and move them to any subdirectory in your home folder.
    *   Can extract archive files if requested.
    *   Can **delete** files if you instruct it to (e.g., *"Delete this file"*).
*   **📂 Auto-Sorting**: Automatically categorizes files (Images, Docs, Videos) if no instruction is provided.
*   **🎨 Customizable UI**: Dark/Light modes, custom colors, and adjustable size.

## 📊 Performance

| Metric | Value |
| :--- | :--- |
| **Memory** | **~46 MB** |
| **CPU** | **< 1%** |
| **Startup** | **Instant** |

## 🛠️ Installation

1.  **Run the installer**:
    ```bash
    ./install.sh
    ```

2.  **Done!**
    *   **Restart**: `systemctl --user restart download-organizer`
    *   **Logs**: `journalctl --user -u download-organizer -f`

## ⚙️ Configuration

### Visual Preferences
Launch the configuration tool:
```bash
./configure_ui.sh
```

![Preferences Window](assets/preferences_demo.png)

### Advanced Config
Edit `src/download_organizer/config.py` to change destination paths.
Edit `src/download_organizer/agent.py` to modify the system prompt.
