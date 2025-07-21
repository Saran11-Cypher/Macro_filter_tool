import os
import subprocess
import time
import sys
import webbrowser

def open_chrome():
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    url = "http://127.0.0.1:8000"
    if os.path.exists(chrome_path):
        subprocess.Popen([chrome_path, url])
    else:
        print("❗ Chrome not found at default path. Opening in default browser instead.")
        webbrowser.open(url)

if __name__ == "__main__":
    os.environ["OFFLINE_MODE"] = "1"

    venv_python = r"C:\Django\Updated_Workspace\.venv\Scripts\python.exe"

    if not os.path.exists(venv_python):
        print("❌ Cannot find virtual environment Python at:", venv_python)
        sys.exit(1)

    print("✅ Launching Django server using:", venv_python)
    subprocess.Popen([venv_python, "manage.py", "runserver", "127.0.0.1:8000"])
    time.sleep(2)
    open_chrome()
