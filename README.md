Here is a clean, professional **README.md** tailored exactly for your Matrix Wi-Fi Scanner project running on Raspberry Pi with a 3.5" touchscreen, intro animation, movie lines, Matrix rain, Wi-Fi HUD, touch-selectable networks, action screens, and the toolbox.

You can copy/paste this directly into GitHub as **README.md**.

---

# 🟩 Matrix Scanner – Raspberry Pi Wi-Fi Security Console

*A Matrix-themed real-time Wi-Fi scanner with animations, touch UI, and penetration-testing toolbox.*

![Matrix](https://upload.wikimedia.org/wikipedia/en/c/c1/The_Matrix_Poster.jpg)

---

## 📌 Overview

**Matrix Scanner** is a fully animated, touchscreen-friendly Wi-Fi awareness tool built for Raspberry Pi.
It features a full Matrix-style interface with intro sequences, real-time scanning, green digital rain, movie-line typing effects, and interactive touch buttons for advanced network actions.

This project is designed **for educational and defensive purposes only** — to visualize nearby Wi-Fi networks, understand digital exposure, and provide quick access to tools often used in penetration-testing labs.

---

## ✨ Features

### 🟢 Core Interface

* Fullscreen Matrix HUD (green terminal aesthetic)
* Custom animated title (“Matrix Proximity Net Scan”)
* Dynamic countdown timer with color-changing gradient
  (green ➝ yellow ➝ red ➝ blinking red)
* Matrix “movie lines” typing animation under the header
* Matrix rain background synced to frame rate
* Smooth scan progress bar and "SCANNING" flash at cycle reset
* Responsive layout for **3.5" ILI9486 touchscreen**

### 🌀 Animations & Intro

* **Wake Up, Neo** boot sequence
* Loader / boot-text simulation
* Combined intro → loader → console chaining
* Random typing mistakes + auto-correction for realism
* Option to show a continuous movie-quotes single-line animator

### 📡 Wi-Fi Scanning HUD

* Real-time Wi-Fi networks list (SSID, RSSI, channel, MAC)
* Touch-selectable networks
* Touch buttons at bottom:

  * **DEAUTH**
  * **CAP HS**
  * **SEND HS**
* Clear action feedback screens

### 🧰 Toolbox Screen

A dedicated MATRIX-THEMED “TOOL BOX”, including categories:

* Network
* Bluetooth
* RFID
* NFC
* USB
* Radio
* OSINT
* Crypto
* System
* IoT
* Protocol

On opening the toolbox:

* Detect installed tools
* Check for available updates
* Log version changes
* Automatically update the internal database

### 🔧 Start-Up Auto-Update (systemd)

On every boot:

* Pull the latest version from GitHub
* Start the Matrix Scanner automatically

---

## 🖥 Hardware Requirements

* **Raspberry Pi 4** (recommended) or Pi 3B/3B+
* **3.5” GPIO Touchscreen** (XPT2046, ILI9486 driver)
* One or more Wi-Fi adapters:

  * *Example:* Alfa AWUS036AXM
  * Supports monitor mode & injection
* (Optional) USB tools for NFC/RFID/Bluetooth/GPS etc.

---

## 📂 File Structure

```
wifi-toy/
├── matrix_console.py
├── matrix_movie_singleline.py
├── matrix_rain_only.py
├── wake_up_neo_intro_backup.py
├── header.py
├── footer.py
└── README.md
```

---

## 🚀 Installation

### 1. Clone the repo:

```bash
git clone https://github.com/sebastian402/Matrix_toy.git ~/wifi-toy
```

### 2. Install dependencies:

```bash
sudo apt update
sudo apt install -y python3-pygame wireless-tools
pip3 install pygame
```

### 3. Run manually:

```bash
DISPLAY=:0 SDL_VIDEODRIVER=x11 python3 ~/wifi-toy/matrix_console.py
```

---

## 🔁 Auto-Update on Boot (systemd)

Create service:

```bash
sudo nano /etc/systemd/system/matrix-toy.service
```

Paste:

```ini
[Unit]
Description=Matrix Toy console
After=network-online.target graphical.target
Wants=network-online.target

[Service]
User=seba
WorkingDirectory=/home/seba/wifi-toy

ExecStartPre=/usr/bin/git -C /home/seba/wifi-toy pull --rebase --autostash

Environment=DISPLAY=:0
Environment=SDL_VIDEODRIVER=x11
ExecStart=/usr/bin/python3 /home/seba/wifi-toy/matrix_console.py

Restart=on-failure

[Install]
WantedBy=graphical.target
```

Enable:

```bash
sudo systemctl daemon-reload
sudo systemctl enable matrix-toy.service
sudo systemctl start matrix-toy.service
```

---

## ⚠️ Legal & Ethical Notice

This project is built **strictly for learning, research, visualization, and defensive cybersecurity**.

Do NOT:

* attack networks you do not own
* capture traffic or handshakes without explicit permission
* attempt unauthorized access

You are 100% responsible for how you use this software.

---

## 🧑‍💻 Author

**Sebastian SMC**
Matrix Wi-Fi Scanner Project — 2025

If you would like me to generate:

* a project logo 🔰
* screenshots
* animated GIF previews
* badges
* a clean ASCII art title
  just tell me and I’ll add them to the README automatically.
