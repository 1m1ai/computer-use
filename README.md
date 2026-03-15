# computer-use — OpenClaw Skill

> AI desktop automation for Windows: mouse, keyboard, screenshot, window control, OCR

An [OpenClaw](https://openclaw.ai) skill that gives your AI agent full control of the local Windows desktop — click, type, take screenshots, focus windows, find UI elements by image, and more.

## What it does

| Action | Description |
|--------|-------------|
| `screenshot` | Capture screen, returns file path |
| `click / rclick / dclick` | Mouse clicks at coordinates |
| `type` | Type text (unicode/CJK safe via clipboard) |
| `key` | Press single key (enter, tab, esc, win…) |
| `hotkey` | Key combinations (ctrl+c, alt+tab…) |
| `scroll` | Scroll at position |
| `drag` | Click-drag between two points |
| `find` | Locate image template on screen |
| `read` | OCR full screen text |
| `winlist` | List all visible window titles |
| `focus` | Bring window to foreground |
| `run` | Launch application or command |
| `getpos` | Get current mouse coordinates |

## Install

### Option A: OpenClaw ClawHub (when available)
```bash
clawhub install computer-use
```

### Option B: Manual
```bash
git clone https://github.com/1m1ai/computer-use.git ~/.openclaw/workspace/skills/computer-use
pip install pyautogui Pillow pyperclip
```

## Usage

The skill is automatically triggered when you ask your agent things like:
- "点击屏幕上的确认按钮"
- "截个图看看现在的状态"
- "打开记事本，输入这段文字"
- "自动化这个操作流程"
- "Click the OK button"
- "Take a screenshot and tell me what you see"

## How it works

The agent follows a **See → Think → Act → Verify** loop:

```
1. screenshot  →  analyse what's on screen
2. decide coordinates or action
3. execute via computer_use.py
4. screenshot again to confirm
5. repeat
```

## Requirements

- Windows 10/11
- Python 3.8+
- `pip install pyautogui Pillow pyperclip`
- Optional OCR: `pip install pytesseract` + [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

## Safety

- **Failsafe active**: move mouse to top-left corner `(0,0)` to abort instantly
- UAC dialogs cannot be automated (Windows security boundary)
- All actions logged with `[OK]` / `[ERR]` / `[WARN]` prefixes

## License

MIT
