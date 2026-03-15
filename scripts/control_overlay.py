#!/usr/bin/env python3
"""
control_overlay.py — 显示"AI正在控制电脑"覆盖层

用法：
  python control_overlay.py show [message]   显示覆盖层（后台运行）
  python control_overlay.py hide             关闭覆盖层
  python control_overlay.py status          检查是否运行中

快捷键：
  ESC          立刻隐藏覆盖层（不终止 AI 任务）
  Ctrl+Shift+Q 立刻终止 AI 控制（写 abort 标志文件）

覆盖层特性：
  - 四个角显示红色"AI控制中"边框
  - 右上角半透明信息面板：当前动作 + 倒计时
  - 始终置顶，不影响点击穿透（WS_EX_TRANSPARENT + WS_EX_LAYERED）
  - 点击穿透：鼠标事件直接传给下层窗口
"""

import sys
import os
import time
import threading
import tempfile
from pathlib import Path

PIDFILE = Path(tempfile.gettempdir()) / "computer_use_overlay.pid"
MSGFILE = Path(tempfile.gettempdir()) / "computer_use_overlay.msg"
ABORTFILE = Path(tempfile.gettempdir()) / "computer_use_abort.flag"

def is_running() -> bool:
    if not PIDFILE.exists():
        return False
    try:
        pid = int(PIDFILE.read_text().strip())
        # check if process alive
        import ctypes
        handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if handle:
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
    except Exception:
        pass
    PIDFILE.unlink(missing_ok=True)
    return False

def write_pid():
    PIDFILE.write_text(str(os.getpid()))

def kill_overlay():
    if not PIDFILE.exists():
        print("[overlay] not running")
        return
    try:
        pid = int(PIDFILE.read_text().strip())
        import ctypes
        handle = ctypes.windll.kernel32.OpenProcess(0x0001, False, pid)
        if handle:
            ctypes.windll.kernel32.TerminateProcess(handle, 0)
            ctypes.windll.kernel32.CloseHandle(handle)
            print(f"[overlay] killed pid {pid}")
        PIDFILE.unlink(missing_ok=True)
    except Exception as e:
        print(f"[overlay] kill failed: {e}")

def run_overlay(message: str = ""):
    """主覆盖层窗口（在独立进程/线程中运行）"""
    try:
        import tkinter as tk
        from tkinter import font as tkfont
    except ImportError:
        print("[ERR] tkinter not available")
        sys.exit(1)

    write_pid()
    ABORTFILE.unlink(missing_ok=True)

    root = tk.Tk()
    root.overrideredirect(True)          # 无边框
    root.attributes("-topmost", True)    # 始终置顶
    root.attributes("-alpha", 0.92)      # 窗口整体不透明度

    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()

    # 只显示右上角信息面板，不全屏覆盖
    PANEL_W = 340
    PANEL_H = 108
    px = sw - PANEL_W - 20
    py = 20
    root.geometry(f"{PANEL_W}x{PANEL_H}+{px}+{py}")

    canvas = tk.Canvas(root, width=PANEL_W, height=PANEL_H,
                       bg="#111111", highlightthickness=2,
                       highlightbackground="#ff3b30")
    canvas.pack(fill="both", expand=True)

    RED = "#ff3b30"
    PANEL_W = 340
    PANEL_H = 108

    # 标题行（红色圆点 + 文字）
    canvas.create_oval(12, 14, 22, 24, fill=RED, outline="")
    canvas.create_text(
        30, 19,
        text="AI 正在控制电脑",
        fill=RED, anchor="w",
        font=("Microsoft YaHei", 12, "bold"),
    )

    # 动作文字
    action_text = canvas.create_text(
        12, 50,
        text=f"▶ {message[:42]}" if message else "▶ 初始化中...",
        fill="#cccccc", anchor="w",
        font=("Microsoft YaHei", 10),
        tags="action"
    )

    # 分割线
    canvas.create_line(12, 72, PANEL_W - 12, 72, fill="#333333")

    # 提示行
    canvas.create_text(
        12, 88,
        text="ESC 隐藏    Ctrl+Shift+Q 立刻终止",
        fill="#555555", anchor="w",
        font=("Microsoft YaHei", 8),
    )

    # 红点脉冲动画
    dot = canvas.find_withtag("") or None
    dot_id = canvas.create_oval(12, 14, 22, 24, fill=RED, outline="")

    pulse_state = [0]
    def pulse():
        pulse_state[0] = (pulse_state[0] + 1) % 20
        alpha = 0.6 + 0.4 * abs(10 - pulse_state[0]) / 10
        color = _blend(RED, "#330000", alpha)
        canvas.itemconfig(dot_id, fill=color)
        # 检查 msg 文件更新
        if MSGFILE.exists():
            try:
                msg = MSGFILE.read_text(encoding="utf-8").strip()
                canvas.itemconfig(action_text, text=f"▶ {msg[:42]}")
            except Exception:
                pass
        # 检查 abort flag
        if ABORTFILE.exists():
            root.destroy()
            return
        root.after(120, pulse)

    def _blend(hex1, hex2, t):
        r1, g1, b1 = int(hex1[1:3],16), int(hex1[3:5],16), int(hex1[5:7],16)
        r2, g2, b2 = int(hex2[1:3],16), int(hex2[3:5],16), int(hex2[5:7],16)
        r = int(r1*t + r2*(1-t))
        g = int(g1*t + g2*(1-t))
        b = int(b1*t + b2*(1-t))
        return f"#{r:02x}{g:02x}{b:02x}"

    # 键盘绑定（需要焦点，但窗口透明；用全局钩子 pynput 作为备选）
    def on_esc(e):
        canvas.delete("panel")
        canvas.delete("corner")

    def on_quit(e):
        ABORTFILE.write_text("abort")
        root.destroy()

    root.bind("<Escape>", on_esc)
    root.bind("<Control-Shift-Q>", on_quit)
    root.bind("<Control-Shift-q>", on_quit)

    # 全局热键（不依赖焦点）—— 用 pynput
    def global_hotkey_thread():
        try:
            from pynput import keyboard
            abort_combo = {keyboard.Key.ctrl_l, keyboard.KeyCode.from_char('Q')}
            abort_combo2 = {keyboard.Key.ctrl_r, keyboard.KeyCode.from_char('Q')}
            current = set()

            def on_press(key):
                current.add(key)
                # ESC → hide panel
                if key == keyboard.Key.esc:
                    root.after(0, lambda: (canvas.delete("panel"), canvas.delete("corner")))
                # Ctrl+Shift+Q → abort
                shift_held = keyboard.Key.shift in current or keyboard.Key.shift_l in current or keyboard.Key.shift_r in current
                ctrl_held = keyboard.Key.ctrl_l in current or keyboard.Key.ctrl_r in current
                q_held = keyboard.KeyCode.from_char('q') in current or keyboard.KeyCode.from_char('Q') in current
                if ctrl_held and shift_held and q_held:
                    ABORTFILE.write_text("abort")
                    root.after(0, root.destroy)

            def on_release(key):
                current.discard(key)

            with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                listener.join()
        except ImportError:
            pass  # pynput not installed, fallback to tkinter bindings only

    t = threading.Thread(target=global_hotkey_thread, daemon=True)
    t.start()

    pulse()
    root.mainloop()
    PIDFILE.unlink(missing_ok=True)


# ── computer_use.py 集成接口 ─────────────────────────────────────────────────

def overlay_show(message: str = ""):
    """在独立进程中显示覆盖层（非阻塞）"""
    import subprocess, sys
    subprocess.Popen(
        [sys.executable, __file__, "show", message],
        creationflags=0x00000008  # DETACHED_PROCESS
    )
    time.sleep(0.3)

def overlay_update(message: str):
    """更新覆盖层显示的动作文字"""
    MSGFILE.write_text(message, encoding="utf-8")

def overlay_hide():
    """关闭覆盖层"""
    kill_overlay()
    MSGFILE.unlink(missing_ok=True)

def overlay_aborted() -> bool:
    """检查用户是否按了 Ctrl+Shift+Q"""
    return ABORTFILE.exists()

def overlay_clear_abort():
    """清除 abort 标志"""
    ABORTFILE.unlink(missing_ok=True)


# ── CLI 入口 ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "show":
        msg = " ".join(args[1:]) if len(args) > 1 else ""
        run_overlay(msg)
    elif args[0] == "hide":
        overlay_hide()
        print("[overlay] hidden")
    elif args[0] == "status":
        print("running" if is_running() else "not running")
    else:
        print(f"Usage: {sys.argv[0]} show [message] | hide | status")
