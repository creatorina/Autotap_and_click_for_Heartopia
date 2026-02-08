import subprocess
import os
import time

SCRIPT_NAME = "auto_tap.py"

def get_modified_time():
    return os.path.getmtime(SCRIPT_NAME)

process = None
last_modified = get_modified_time()

def start_script():
    print("▶ Starting auto_tap.py")
    return subprocess.Popen(["python", SCRIPT_NAME])

process = start_script()

while True:
    time.sleep(1)

    try:
        new_time = get_modified_time()

        if new_time != last_modified:
            print("🔄 Script changed, restarting...")

            last_modified = new_time

            process.kill()
            process = start_script()

    except KeyboardInterrupt:
        process.kill()
        break
