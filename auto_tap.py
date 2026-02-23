import pyautogui
import cv2
import numpy as np
import time
import os
import keyboard
import threading
import sys

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ================= KONFIGURASI =================
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = False

running = False
pause_event = threading.Event()

mode = "click"
target_key = "f"		# ======== SETTING BUTTON KEY
key_press_count = 1		# ======== SETING HOW MANY TIMES
cooldown_after_key = 2.1	# ======== COOLDOWN AFTER KEY

template_folder = "templates"
script_path = os.path.abspath(__file__)
# ===============================================

templates = []
clicked_positions = []
reload_lock = False
watchdog_active = True
last_snapshot = set()
poll_interval = 3


# ================= STATUS DISPLAY =================
def print_status():
    print("\n" + "-" * 35)
    print("HOTKEYS CONTROL:")
    print("6 = PLAY")
    print("7 = PAUSE")
    print("8 = MODE CLICK MOUSE")
    print("9 = MODE KEY (" + target_key.upper() + ")")
    print("-" * 35)

    if running:
        print("▶ STATUS : RUNNING | MODE :", mode.upper())
    else:
        print("⏸ STATUS : PAUSED")

    print("-" * 35 + "\n")


# ================= TEMPLATE LOADER =================
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
    print_status()


# ================= WATCH TEMPLATE =================
class TemplateWatcher(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.src_path.endswith(".png"):
            load_templates()


# ================= AUTO RESTART WHEN SAVE =================
class ScriptWatcher(FileSystemEventHandler):
    def on_modified(self, event):
        if os.path.abspath(event.src_path) == script_path:
            print("\n⚡ Script upgraded! Restarting...\n")
            time.sleep(0.5)
            os.execv(sys.executable, [sys.executable] + sys.argv)


def start_watchdog():
    global watchdog_active
    try:
        observer = Observer()
        observer.schedule(TemplateWatcher(), template_folder, recursive=False)
        observer.schedule(ScriptWatcher(), ".", recursive=False)
        observer.start()
        print("Watchdog realtime aktif ✔")
        while True:
            time.sleep(1)
    except:
        watchdog_active = False


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


def is_close(pos, pos_list, distance=40):
    for p in pos_list:
        if abs(pos[0] - p[0]) < distance and abs(pos[1] - p[1]) < distance:
            return True
    return False


# ================= VERIFIKASI SEBELUM KLIK =================
def verify_target(template, x, y, w, h):
    try:
        reg_x, reg_y = int(x - w//2), int(y - h//2)
        screenshot = pyautogui.screenshot(region=(reg_x, reg_y, w, h))
        check_screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(check_screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)

        return max_val >= 0.80
    except:
        return False


# ================= INIT =================
if not os.path.exists(template_folder):
    os.makedirs(template_folder)

load_templates()
last_snapshot = set(os.listdir(template_folder))

threading.Thread(target=start_watchdog, daemon=True).start()
threading.Thread(target=polling_watcher, daemon=True).start()

print_status()


# ================= MAIN LOOP =================
try:
    while True:

        if keyboard.is_pressed("6"):
            running = True
            pause_event.clear()
            print_status()
            time.sleep(0.2)

        if keyboard.is_pressed("7"):
            running = False
            pause_event.set()   # STOP
            print_status()
            time.sleep(0.2)

        if keyboard.is_pressed("8"):
            mode = "click"
            print_status()
            time.sleep(0.2)

        if keyboard.is_pressed("9"):
            mode = "key"
            print_status()
            time.sleep(0.2)

        if not running:
            time.sleep(0.005)
            continue

        screenshot = pyautogui.screenshot()
        screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)

        found_any = False
        clicked_positions.clear()

        for name, template in templates:

            if pause_event.is_set():
                break

            w, h = template.shape[::-1]
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(result >= 0.80)

            for pt in zip(*loc[::-1]):

                if pause_event.is_set():
                    break

                x = pt[0] + w // 2
                y = pt[1] + h // 2

                if is_close((x, y), clicked_positions):
                    continue

                if not verify_target(template, x, y, w, h):
                    continue

                found_any = True
                clicked_positions.append((x, y))

                if mode == "click":
                    pyautogui.moveTo(x, y, duration=0.01)	# === SPEED MOVE POINTER
                    pyautogui.mouseDown()
                    time.sleep(0.01)				# === SPEED CLICK
                    pyautogui.mouseUp()
                else:
                    for _ in range(key_press_count):
                        keyboard.press_and_release(target_key)
                    time.sleep(cooldown_after_key)
                    break

                time.sleep(0.005)

        if not found_any:
            time.sleep(0.005)			# === SPEED SCAN SCREEN

except Exception as e:
    print("Runtime error:", e)
