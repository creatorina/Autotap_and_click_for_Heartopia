import pyautogui
import cv2
import numpy as np
import time
import os
import keyboard
import threading

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

running = False
templates = []
template_folder = "templates"
clicked_positions = []

reload_lock = False
watchdog_active = True

last_snapshot = set()
poll_interval = 3


# ===== LOAD TEMPLATE FUNCTION =====
def load_templates():
    global templates, reload_lock

    if reload_lock:
        return

    reload_lock = True

    try:
        templates.clear()

        if not os.path.exists(template_folder):
            os.makedirs(template_folder)

        print("\nReloading templates...")

        for file in os.listdir(template_folder):
            if file.endswith(".png"):
                path = os.path.join(template_folder, file)
                img = cv2.imread(path, 0)

                if img is not None:
                    templates.append((file, img))
                    print("Loaded:", file)

        print("Total Template:", len(templates))

    except Exception as e:
        print("Template load error:", e)

    reload_lock = False


# ===== WATCHDOG HANDLER =====
class TemplateWatcher(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.src_path.endswith(".png"):
            load_templates()


# ===== START WATCHDOG SAFE =====
def start_watchdog():
    global watchdog_active

    try:
        observer = Observer()
        observer.schedule(TemplateWatcher(), template_folder, recursive=False)
        observer.start()

        print("Watchdog realtime aktif ✔")

        while True:
            time.sleep(1)

    except Exception as e:
        print("Watchdog crash → fallback polling")
        watchdog_active = False


# ===== POLLING FALLBACK =====
def polling_watcher():
    global last_snapshot

    while True:

        if watchdog_active:
            time.sleep(2)
            continue

        try:
            current = set(os.listdir(template_folder))

            if current != last_snapshot:
                last_snapshot = current
                load_templates()

        except:
            pass

        time.sleep(poll_interval)


# ===== PASTIKAN FOLDER ADA =====
if not os.path.exists(template_folder):
    os.makedirs(template_folder)

load_templates()
last_snapshot = set(os.listdir(template_folder))


# ===== START WATCHERS =====
threading.Thread(target=start_watchdog, daemon=True).start()
threading.Thread(target=polling_watcher, daemon=True).start()


def is_close(pos, pos_list, distance=40):
    for p in pos_list:
        if abs(pos[0] - p[0]) < distance and abs(pos[1] - p[1]) < distance:
            return True
    return False


print("6 = PLAY")
print("7 = PAUSE")
print("8 = EXIT")

# ===== LOOP =====
try:
    while True:

        if keyboard.is_pressed("6"):
            running = True
            print("▶ RUNNING")
            time.sleep(0.3)

        if keyboard.is_pressed("7"):
            running = False
            print("⏸ PAUSED")
            time.sleep(0.3)

        if keyboard.is_pressed("8"):
            print("❌ EXIT")
            break

        if not running:
            time.sleep(0.01)
            continue

        screenshot = pyautogui.screenshot()
        screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)

        found_any = False
        clicked_positions.clear()

        for name, template in templates:

            w, h = template.shape[::-1]

            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(result >= 0.80)

            for pt in zip(*loc[::-1]):

                x = pt[0] + w // 2
                y = pt[1] + h // 2

                if is_close((x, y), clicked_positions):
                    continue

                found_any = True
                clicked_positions.append((x, y))

                # =====KECEPATAN PERPINDAHAN======
                pyautogui.moveTo(x, y, duration=0.01)
                time.sleep(0.01)

                # =====KECEPATAN KLIK=============
                pyautogui.mouseDown()
                time.sleep(0.01)
                pyautogui.mouseUp()

                # =====DELAY SETIAP SESSION=======
                time.sleep(0.05)
	
	# ==========KECEPATAN SCAN AREA==========
        if not found_any:
            time.sleep(0.1)

except Exception as e:
    print("Runtime error:", e)
