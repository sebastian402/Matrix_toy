# Matrix Toy

Matrix-themed Raspberry Pi dashboard that chains a wake-up intro, Matrix rain transition, and touchscreen-friendly Wi-Fi console. Each stage runs fullscreen at 480×320 and is orchestrated by the `matrix_main.py` launcher.

## Scripts
- `matrix_main.py` – launcher that can list available scripts, skip stages, and pause between them while running each script in its own Python process to avoid pygame state reuse.
- `wake_up_neo_intro_backup.py` – Neo-style boot intro with staged typing and loader effects before the console.
- `matrix_rain_only.py` – self-contained Matrix rain transition used between intro and console.
- `matrix_console.py` – main Wi-Fi HUD: runs periodic `nmcli` scans, renders network rows with signal bars, lets you toggle lab devices, and shows animated header/movie line plus the footer ticker.
- `footer.py` – scrolling system-info ticker (LAN/Public IP, model, OS, geo, time) with cached renders to reduce per-frame work.
- `header.py` – animated title and countdown indicator with dehashing effect and color gradients.

## Requirements
- Python 3 with `pygame` installed (used by all visual stages).
- NetworkManager (`nmcli`) available for Wi-Fi scanning in the console.
- Access to system utilities like `hostname`, `/etc/os-release`, and `curl` for footer data; failures are handled gracefully.

## Running
Run all stages in sequence:

```bash
python3 matrix_main.py
```

Useful flags:
- `--skip-intro`, `--skip-rain`, `--skip-console` – skip stages when testing.
- `--pause SECONDS` – wait between stages (handy when debugging).
- `--list-files` – print discovered Python scripts before running the chain.

If you only want the console, run it directly (ensuring a display driver is configured):

```bash
python3 matrix_console.py
```

## Install from your PC to the Pi over SSH (commands only)
Run these from your PC terminal (replace `<PI_IP>` and the local path to the project):

```bash
PI_HOST=pi@<PI_IP>
PI_DIR=/home/pi/Matrix_toy

ssh "$PI_HOST" "sudo apt-get update && sudo apt-get install -y python3-pygame network-manager curl git"
scp -r /path/to/Matrix_toy "$PI_HOST:$PI_DIR"
ssh "$PI_HOST" "cd $PI_DIR && PYGAME_HIDE_SUPPORT_PROMPT=1 python3 matrix_main.py --skip-intro --skip-rain"
ssh "$PI_HOST" "cd $PI_DIR && PYGAME_HIDE_SUPPORT_PROMPT=1 python3 matrix_main.py"
```

## Data files
The console stores network discovery history and lab flags beside the code for easy persistence on the Pi:
- `discovered_devices.json` – networks seen with timestamps and signal strength.
- `lab_devices.json` – toggled lab device flags synced with discovered networks.

## Notes
- All stages expect a 480×320 display; the Pi touchscreen fits this by default.
- ESC or `q` exits the console; `r` triggers an immediate rescan.
- Touch/mouse clicks on a network row toggle its lab flag for quick lab device marking.

## Codex description (constraints to keep)
- IMPORTANT: do not modify `header.py` or overwrite header animations. Version tag support is required. Auto-update launcher script must remain intact. Do not strip out the `version_text` argument from `draw_header()`.
- Codex: `header.py` now includes `version_text` support and countdown simplification. `matrix_console.py` now passes `APP_VERSION`. Auto-update is handled by `update_and_run.sh`. These features must never be removed.

## Pushing to GitHub
This environment currently has no Git remotes configured. To publish your changes:

1. Create a repo on GitHub (or reuse an existing one) and note its SSH or HTTPS URL.
2. Add the remote here:
   ```bash
   git remote add origin <your-repo-url>
   ```
3. Push the local branch (replace `work` if you prefer another name):
   ```bash
   git push -u origin work
   ```
4. Future pushes can use `git push` without extra flags. Use `git status` to confirm a clean tree before pushing.
