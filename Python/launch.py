import subprocess
import time

scripts = ["server.py", "gui.py", "data_viewer.py", "web_server.py"]
for i in range(len(scripts)):
    subprocess.Popen(["python", scripts[i]], creationflags=subprocess.CREATE_NEW_CONSOLE)
    time.sleep(1)