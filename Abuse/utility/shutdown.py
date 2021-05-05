# Method for shutting down various systems
import platform


def shutdown():
    """
    Shutdown system based on OS
    """
    print("[*] Shutting down.")
    plat = platform.platform().lower()

    if plat.startswith("linux"):
        import subprocess
        subprocess.call("sudo shutdown -h now", shell=True)

    elif plat.startswith("windows"):
        import os
        os.system("shutdown /s /t 1")

    else:
        print("[!] System not supported fro shutdown")
