# Method for shutting down various systems
import os
import platform
import subprocess


def shutdown():
    """Shutdown system based on OS."""
    print("[*] Shutting down.")
    plat = platform.platform().lower()

    if plat.startswith("linux"):
        subprocess.call("sudo shutdown -h now", shell=True)

    elif plat.startswith("windows"):
        os.system("shutdown /s /t 1")

    else:
        print("[!] System not supported fro shutdown")
