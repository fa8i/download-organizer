import sys
import os
import subprocess

try:
    import gi
    gi.require_version('Notify', '0.7')
    from gi.repository import Notify, GLib
except ImportError:
    # Fallback to system packages if not in venv
    sys.path.append("/usr/lib/python3/dist-packages")
    import gi
    gi.require_version('Notify', '0.7')
    from gi.repository import Notify, GLib

def on_notification_action(n, action, folder):
    """Callback for the 'open' action."""
    import shutil
    
    if folder and os.path.exists(folder):
        # List of common file managers to try first
        # This prevents opening in VS Code or other editors that might claim inode/directory
        file_managers = ["nautilus", "dolphin", "nemo", "thunar", "pcmanfm", "caja"]
        
        opened = False
        for fm in file_managers:
            if shutil.which(fm):
                try:
                    subprocess.run([fm, folder])
                    opened = True
                    break
                except Exception:
                    continue
        
        if not opened:
            # Use gio open which is more reliable in GTK/GNOME environments
            try:
                subprocess.run(["gio", "open", folder], check=True)
            except Exception:
                # Fallback to xdg-open silently
                subprocess.run(["xdg-open", folder])
    n.close()
    loop.quit()

def on_notification_closed(n):
    """Callback when notification is dismissed."""
    loop.quit()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python notification.py <title> <message> [folder_path] [icon]")
        sys.exit(1)
    
    title = sys.argv[1]
    message = sys.argv[2]
    folder_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Try to get icon from config if not provided
    icon = None
    if len(sys.argv) > 4:
        icon = sys.argv[4]
    else:
        try:
            from ..config import APP_ICON
            icon = APP_ICON
        except:
            icon = "folder-remote"

    Notify.init("Download Organizer")
    
    # Create notification
    n = Notify.Notification.new(title, message, icon)
    
    # Add action if folder provided
    if folder_path:
        # Using "default" action name allows clicking the notification body.
        # Although often hidden, the label must not be empty.
        n.add_action("default", "Abrir carpeta", on_notification_action, folder_path)
    
    n.connect("closed", on_notification_closed)
    
    try:
        n.show()
        loop = GLib.MainLoop()
        # Set a timeout just in case it hangs
        GLib.timeout_add_seconds(60, loop.quit)
        loop.run()
    except Exception as e:
        print(f"Error showing notification: {e}")
        sys.exit(1)
