# Computer Use — Workflow Patterns

## Standard Loop: See → Think → Act → Verify

Every task follows this loop:

```
1. screenshot → analyse what's on screen
2. decide action (click / type / hotkey)
3. execute action via computer_use.py
4. screenshot again → confirm result
5. repeat until done
```

Never chain more than 3 actions without a screenshot to confirm state.

---

## Finding Click Targets

### By coordinates (known layout)
```bash
python computer_use.py click 960 540
```

### By image template (reliable for buttons/icons)
```bash
# Save a crop of the button first, then:
python computer_use.py find assets/ok_button.png
# → prints "423 311"
python computer_use.py click 423 311
```

### By window focus + keyboard (most reliable for apps)
```bash
python computer_use.py focus "Notepad"
python computer_use.py hotkey ctrl a
python computer_use.py type "Hello world"
```

---

## Common Recipes

### Open application
```bash
python computer_use.py run "notepad.exe"
python computer_use.py run "C:\Program Files\App\app.exe"
```

### Type text with Enter
```bash
python computer_use.py type "search query"
python computer_use.py key enter
```

### Copy selected text
```bash
python computer_use.py hotkey ctrl a   # select all
python computer_use.py hotkey ctrl c   # copy
# then read clipboard in Python: import pyperclip; pyperclip.paste()
```

### Close window
```bash
python computer_use.py hotkey alt F4
```

### Switch window
```bash
python computer_use.py hotkey alt tab
```

### Scroll down in a document
```bash
python computer_use.py scroll 960 540 -5   # scroll down 5 clicks
python computer_use.py scroll 960 540 5    # scroll up 5 clicks
```

### File save dialog
```bash
python computer_use.py hotkey ctrl s          # trigger save dialog
python computer_use.py screenshot             # verify dialog open
python computer_use.py type "C:\output.txt"   # type path
python computer_use.py key enter
```

---

## Coordinate Tips

- Get resolution: `python -c "import pyautogui; print(pyautogui.size())"`
- Get current mouse pos: `python computer_use.py getpos`
- Move mouse to inspect: `python computer_use.py move <x> <y>` then take screenshot

Standard 1920×1080 reference points:
- Screen center: `960 540`
- Taskbar (bottom): `y ≈ 1060`
- Top-left corner (failsafe!): `0 0`

---

## Error Handling

| Output | Meaning |
|--------|---------|
| `[OK] ...` | Success |
| `[WARN] ...` | Non-fatal warning |
| `[ERR] ...` | Error, exit code 1 |
| `[NOT_FOUND]` | Image template not found on screen |
| `[INSTALL] pip install ...` | Missing dependency |

On `[ERR]`: take a fresh screenshot and reassess — screen state may have changed.

---

## Safety Notes

- **Failsafe**: Moving mouse to top-left `(0, 0)` instantly aborts pyautogui
- Never type passwords in plain shell commands (visible in process list) — use clipboard method
- Test with `move` before `click` on critical targets
- On Windows: UAC dialogs cannot be automated (security boundary)
