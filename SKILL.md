---
name: computer-use
description: >
  Control the local computer programmatically: move mouse, click, type text
  (including CJK/unicode), press hotkeys, drag, scroll, focus windows, launch
  apps, find UI elements by image template, and OCR the screen.
  Use when the user asks you to automate desktop tasks, click buttons, fill
  forms, open applications, operate GUI software, take screenshots for
  analysis, or perform any mouse/keyboard action on the host machine.
  Requires pyautogui and Pillow (auto-installs on first run check).
---

# Computer Use

Control the host machine via `scripts/computer_use.py`.

## Quick Start

```bash
$py = "C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe"
$script = "path\to\skills\computer-use\scripts\computer_use.py"

# Install deps (one-time)
& $py -m pip install pyautogui Pillow pyperclip

# Take screenshot
& $py $script screenshot
# → prints path like C:\...\shot_1234567890.png

# Click at coordinates
& $py $script click 960 540

# Type text (supports Chinese/unicode via clipboard)
& $py $script type "你好 Hello"

# Press key
& $py $script key enter

# Hotkey
& $py $script hotkey ctrl s
```

## Standard Workflow: See → Think → Act → Verify

1. `screenshot` → read image to understand current screen state
2. Decide coordinates or action from what you see
3. Execute action (click/type/hotkey/etc.)
4. `screenshot` again to confirm result
5. Repeat

**Never skip the verify step on important actions.**

## All Actions

| Action | Syntax | Notes |
|--------|--------|-------|
| `screenshot` | `screenshot [path]` | Returns file path |
| `click` | `click <x> <y>` | Left click |
| `rclick` | `rclick <x> <y>` | Right click |
| `dclick` | `dclick <x> <y>` | Double click |
| `move` | `move <x> <y>` | Move mouse only |
| `type` | `type <text>` | Unicode-safe via clipboard |
| `key` | `key <key>` | Single key (enter/tab/esc/win/f1…) |
| `hotkey` | `hotkey ctrl c` | Key combination |
| `scroll` | `scroll <x> <y> <n>` | +n=up, -n=down |
| `drag` | `drag <x1> <y1> <x2> <y2>` | Click-drag |
| `find` | `find <template.png> [conf]` | Image template match, returns `x y` |
| `read` | `read` | OCR full screen (needs pytesseract) |
| `winlist` | `winlist` | List visible window titles |
| `focus` | `focus <title_substr>` | Bring window to foreground |
| `run` | `run <cmd>` | Launch app/command |
| `getpos` | `getpos` | Print current mouse x y |

## Finding Click Targets

**Preferred method**: `screenshot` → analyse image → use coordinates directly.

**Image template method** (when coordinates are unknown/variable):
```bash
# 1. Take screenshot, crop the button/icon to a small PNG, save as template
& $py $script find "path\to\template.png"
# → "423 311"  (center of match)
& $py $script click 423 311
```

**Window + keyboard** (most reliable for text input):
```bash
& $py $script focus "Chrome"
& $py $script hotkey ctrl l
& $py $script type "https://example.com"
& $py $script key enter
```

## Dependency Installation

```powershell
$py = "C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe"
& $py -m pip install pyautogui Pillow pyperclip

# Optional: OCR support
& $py -m pip install pytesseract
# + install Tesseract OCR from https://github.com/UB-Mannheim/tesseract/wiki
```

## Safety

- **Failsafe active**: move mouse to top-left corner `(0,0)` to immediately abort
- UAC dialogs on Windows cannot be automated (OS security boundary)
- Test coordinates with `move` before `click` on critical targets

## Workflow Patterns

See `references/workflow-patterns.md` for recipes: open apps, file save dialogs,
copy/paste, scrolling, window switching, and error handling.
