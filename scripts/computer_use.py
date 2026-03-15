#!/usr/bin/env python3
"""
computer_use.py — AI-driven computer control via pyautogui + PIL + subprocess
Usage: python computer_use.py <action> [args...]

Actions:
  screenshot [path]          Take screenshot, print path
  click <x> <y>              Left-click at coordinates
  rclick <x> <y>             Right-click at coordinates
  dclick <x> <y>             Double-click at coordinates
  move <x> <y>               Move mouse (no click)
  type <text>                Type text (supports unicode via clipboard)
  key <key>                  Press key (enter, tab, esc, win, etc.)
  hotkey <k1> <k2> ...       Press key combination
  scroll <x> <y> <clicks>    Scroll at position (positive=up, negative=down)
  drag <x1> <y1> <x2> <y2>  Drag from (x1,y1) to (x2,y2)
  find <template.png>        Find template image on screen, print center x,y
  read                       OCR current screen, print text
  winlist                    List visible window titles
  focus <title_substr>       Focus window by title substring
  run <cmd>                  Launch application/command
  getpos                     Print current mouse position
"""

import sys
import os
import time
import json
import subprocess
import tempfile
from pathlib import Path

# ── dependency check ────────────────────────────────────────────────────────
def check_deps():
    missing = []
    for pkg in ["pyautogui", "PIL"]:
        try:
            __import__(pkg if pkg != "PIL" else "PIL.Image")
        except ImportError:
            missing.append("pyautogui" if pkg == "pyautogui" else "Pillow")
    if missing:
        print(f"[INSTALL] pip install {' '.join(missing)}", flush=True)
        sys.exit(1)

check_deps()

import pyautogui
from PIL import Image, ImageGrab

pyautogui.FAILSAFE = True   # move mouse to top-left corner to abort
pyautogui.PAUSE = 0.15      # small pause between actions for stability

SCREENSHOT_DIR = Path(tempfile.gettempdir()) / "computer_use_shots"
SCREENSHOT_DIR.mkdir(exist_ok=True)

# ── helpers ────────────────────────────────────────────────────────��─────────
def screenshot(path: str = None) -> str:
    if not path:
        path = str(SCREENSHOT_DIR / f"shot_{int(time.time())}.png")
    img = ImageGrab.grab()
    img.save(path)
    return path

def type_unicode(text: str):
    """Type text including CJK characters via clipboard."""
    import subprocess, time
    # Try pyautogui first (ASCII fast path)
    if all(ord(c) < 128 for c in text):
        pyautogui.typewrite(text, interval=0.04)
        return
    # Unicode: paste via clipboard
    try:
        import pyperclip
        pyperclip.copy(text)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.2)
    except ImportError:
        # Fallback: PowerShell Set-Clipboard
        escaped = text.replace("'", "''")
        subprocess.run(
            ["powershell", "-Command", f"Set-Clipboard -Value '{escaped}'"],
            capture_output=True
        )
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.2)

def find_window(substr: str):
    """Return hwnd of first visible window whose title contains substr (Windows)."""
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    result = []
    def cb(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            if substr.lower() in buf.value.lower():
                result.append((hwnd, buf.value))
        return True
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_size_t, ctypes.c_size_t)
    user32.EnumWindows(WNDENUMPROC(cb), 0)
    return result

def list_windows():
    """List all visible window titles."""
    import ctypes
    user32 = ctypes.windll.user32
    titles = []
    def cb(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buf, length + 1)
                titles.append(buf.value)
        return True
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_size_t, ctypes.c_size_t)
    user32.EnumWindows(WNDENUMPROC(cb), 0)
    return titles

def focus_window(substr: str) -> bool:
    """Bring window matching substr to foreground."""
    import ctypes
    wins = find_window(substr)
    if not wins:
        print(f"[WARN] No window found matching: {substr}")
        return False
    hwnd, title = wins[0]
    user32 = ctypes.windll.user32
    # Restore if minimized
    user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.3)
    print(f"[OK] Focused: {title}")
    return True

def find_image_on_screen(template_path: str, confidence: float = 0.8):
    """Locate template image on screen. Returns (x, y) center or None."""
    try:
        loc = pyautogui.locateOnScreen(template_path, confidence=confidence)
        if loc:
            cx = loc.left + loc.width // 2
            cy = loc.top + loc.height // 2
            return cx, cy
    except Exception as e:
        print(f"[ERR] find: {e}")
    return None

def ocr_screen() -> str:
    """Read text from screen using pytesseract (optional dep)."""
    try:
        import pytesseract
        img = ImageGrab.grab()
        text = pytesseract.image_to_string(img, lang="chi_sim+eng")
        return text.strip()
    except ImportError:
        return "[ERR] pytesseract not installed. pip install pytesseract + install Tesseract OCR"
    except Exception as e:
        return f"[ERR] OCR failed: {e}"

# ── main dispatch ────────────────────────────────────────────────────────────
def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    action = args[0].lower()

    try:
        if action == "screenshot":
            path = args[1] if len(args) > 1 else None
            result = screenshot(path)
            print(result)

        elif action == "click":
            x, y = int(args[1]), int(args[2])
            pyautogui.click(x, y)
            print(f"[OK] click ({x}, {y})")

        elif action == "rclick":
            x, y = int(args[1]), int(args[2])
            pyautogui.rightClick(x, y)
            print(f"[OK] rclick ({x}, {y})")

        elif action == "dclick":
            x, y = int(args[1]), int(args[2])
            pyautogui.doubleClick(x, y)
            print(f"[OK] dclick ({x}, {y})")

        elif action == "move":
            x, y = int(args[1]), int(args[2])
            pyautogui.moveTo(x, y, duration=0.3)
            print(f"[OK] move ({x}, {y})")

        elif action == "type":
            text = " ".join(args[1:])
            type_unicode(text)
            print(f"[OK] typed {len(text)} chars")

        elif action == "key":
            key = args[1]
            pyautogui.press(key)
            print(f"[OK] key {key}")

        elif action == "hotkey":
            keys = args[1:]
            pyautogui.hotkey(*keys)
            print(f"[OK] hotkey {'+'.join(keys)}")

        elif action == "scroll":
            x, y, clicks = int(args[1]), int(args[2]), int(args[3])
            pyautogui.scroll(clicks, x=x, y=y)
            print(f"[OK] scroll {clicks} at ({x}, {y})")

        elif action == "drag":
            x1, y1, x2, y2 = int(args[1]), int(args[2]), int(args[3]), int(args[4])
            pyautogui.moveTo(x1, y1, duration=0.3)
            pyautogui.dragTo(x2, y2, duration=0.5, button="left")
            print(f"[OK] drag ({x1},{y1}) → ({x2},{y2})")

        elif action == "find":
            template = args[1]
            confidence = float(args[2]) if len(args) > 2 else 0.8
            result = find_image_on_screen(template, confidence)
            if result:
                print(f"{result[0]} {result[1]}")
            else:
                print("[NOT_FOUND]")
                sys.exit(1)

        elif action == "read":
            print(ocr_screen())

        elif action == "winlist":
            titles = list_windows()
            for t in titles:
                print(t)

        elif action == "focus":
            substr = " ".join(args[1:])
            ok = focus_window(substr)
            sys.exit(0 if ok else 1)

        elif action == "run":
            cmd = " ".join(args[1:])
            subprocess.Popen(cmd, shell=True)
            print(f"[OK] launched: {cmd}")
            time.sleep(1)

        elif action == "getpos":
            x, y = pyautogui.position()
            print(f"{x} {y}")

        else:
            print(f"[ERR] Unknown action: {action}")
            print(__doc__)
            sys.exit(1)

    except IndexError:
        print(f"[ERR] Missing arguments for action: {action}")
        print(__doc__)
        sys.exit(1)
    except Exception as e:
        print(f"[ERR] {action} failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
