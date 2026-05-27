<div align="center">

# Smart Download Organizer

![Python Version](https://img.shields.io/badge/python-3.12-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/platform-linux-black?style=for-the-badge&logo=linux)
![Ubuntu](https://img.shields.io/badge/tested%20on-Ubuntu%2026.04-orange?style=for-the-badge&logo=ubuntu)
![License](https://img.shields.io/badge/license-MIT-purple?style=for-the-badge)

**AI-powered assistant that keeps your `Downloads` folder organized.**  
Powered by [**Agentify**](https://github.com/fa8i/Agentify).

</div>

---

## Overview

**Smart Download Organizer** runs silently in the background and watches your downloads folder.  
When a new file appears, it shows a small dialog where you can write what you want to do with that file.

For example:

> Move this to invoices and rename it to Invoice_January

If you do not write anything, the app automatically organizes the file by type.

> [!NOTE]
> **Linux only.**  
> This version is tested on **Ubuntu 26.04 with GNOME Wayland**.
>
> The app starts with your desktop session using **GNOME Autostart**. It does not use a `systemd --user` service because interactive popups are more reliable this way on Wayland.

![Smart Download Organizer Demo](assets/pic_demo.png)

---

## Features

* **AI-powered file organization**
  * Understands natural-language instructions.
  * Can move, rename, delete, extract, and organize files.
  * Uses [Agentify](https://github.com/fa8i/Agentify) to connect with different LLM providers.

* **Automatic sorting**
  * If no instruction is provided, files are sorted automatically by type.

* **Desktop popup**
  * Shows a small dialog when a new download is detected.

* **Customizable UI**
  * Includes visual preferences such as theme, colors, and size.

---

## Installation

1. Clone the repository:

    git clone https://github.com/fa8i/download-organizer.git
    cd download-organizer

2. Run the installer:

    ./install.sh

The installer will:

* Install required Linux packages.
* Install `uv` if needed.
* Create a Python 3.12 virtual environment.
* Install Python dependencies.
* Create the desktop autostart entry.
* Start the app.

That is all.

---

## Configuration

Create your `.env` file:

    cp .env.example .env
    nano .env

Configure your LLM provider, model, and API key.

Example:

    LLM_PROVIDER=openai
    LLM_MODEL=gpt-4.1-mini
    OPENAI_API_KEY=your_api_key_here

The supported providers depend on your Agentify configuration.

---

## Visual Preferences

Launch the configuration tool:

    ./configure_ui.sh

![Preferences Window](assets/preferences_demo.png)

---

## Usage

After installation, the app starts automatically when you log into GNOME.

To test it, create a file in your downloads folder:

    echo "test" > "$(xdg-user-dir DOWNLOAD)/test_download_organizer.txt"

A popup should appear.

---

## Logs

View live logs:

    tail -f ~/.cache/download-organizer/app.log

---

## Start and Stop

Start manually:

    ./run_download_organizer.sh

Stop the app:

    pkill -f "download_organizer/main.py"

The app will start again automatically the next time you log in.

---

## Troubleshooting

### The popup does not appear

Check that the app is running:

    ps -ef | grep "download_organizer/main.py" | grep -v grep

Check logs:

    tail -f ~/.cache/download-organizer/app.log

Start manually from the project folder:

    ./run_download_organizer.sh

### The AI request fails

If you see an error like:

    429 Too Many Requests
    insufficient_quota

your LLM provider rejected the request due to quota, billing, or rate limits.  
Check your API key, billing status, or use another provider supported by Agentify.

### Reinstall cleanly

If something breaks after a system upgrade:

    pkill -f "download_organizer/main.py" 2>/dev/null || true
    mv venv venv.broken-$(date +%F-%H%M%S)
    ./install.sh

---

## Notes for Ubuntu 26.04 / Wayland

This version uses **GNOME Autostart** instead of `systemd --user`.

This is intentional: on GNOME Wayland, desktop popups launched from systemd services may not appear or may not be positioned correctly. Running the app as part of the desktop session gives better behavior for interactive dialogs.

---

## License

MIT
