"""Single-line Matrix quote renderer with typing mistakes and blinking cursor."""

from __future__ import annotations

import random
import sys
from typing import List, Tuple

import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 480, 320
BLACK: Tuple[int, int, int] = (0, 0, 0)
GREEN: Tuple[int, int, int] = (0, 255, 0)
WHITE: Tuple[int, int, int] = (255, 255, 255)
FONT_NAME = "dejavusansmono"
FONT_SIZE = 12
LINE_X = 10
LINE_Y = 10
TYPE_MIN_DELAY_MS = 30
TYPE_MAX_DELAY_MS = 90
MISTAKE_MIN_DELAY_MS = 30
MISTAKE_MAX_DELAY_MS = 90
BLINK_ON_MS = 250
BLINK_OFF_MS = 200
BLINK_COUNT = 3
MISTAKE_PROBABILITY = 0.12
MISTAKE_CHARS: List[str] = list("abcdefghijklmnopqrstuvwxyz0123456789#$%&*+-=/<>")

LINES = [
    "Wake up, Neo.", "The Matrix has you.", "Follow the white rabbit.",
    "There is no spoon.", "What is real, anyway?",
    "Blue pill or red pill today?", "Welcome to the real world.",
    "Glitches are just clues in the code.",
    "Agents are reading the logs right now.",
    "They still use default passwords???",
    "Never trust a Wi-Fi named 'Free_Public_WiFi'.",
    "Your firewall called, it wants rules, not hope.",
    "Root access is a responsibility, not a toy.",
    "Encryption is just math wearing a trench coat.",
    "The safest password is the one you rotate.",
    "Curiosity opened more ports than nmap ever did.",
    "The spoon bends because the code says so.",
    "Reality is just a very stable simulation.",
    "Someone hardcoded credentials in production. Again.",
    "Backups are proof you believe in failure.",
    "The system is down. Or maybe awake.",
    "Never underestimate a bored teenager with Wi-Fi.",
    "The Oracle speaks in stack traces.",
    "Your ISP knows what you did last summer.",
    "Patches today, fewer breaches tomorrow.",
    "Trust, but verify the checksum.",
    "Social engineering bypasses any firewall.",
    "The first rule: check the cables.",
    "Misconfigured DNS is the real Architect.",
    "There is no cloud, just other people's computers.",
    "You can dodge bullets, but not updates.",
    "The Matrix runs on undocumented features.",
    "Hope is not an incident response plan.",
    "You are not behind a VPN, Neo.",
    "Someone turned off logging to fix lag.",
    "Strong password, weak endpoint. Classic.",
    "Every unsecured camera tells a story.",
    "Two-factor or two-regret authentication.",
    "The cake was a lie, the hash too.",
    "Access denied is just a challenge message.",
    "The rabbit hole starts at port 80.",
    "Compliance is not the same as security.",
    "Air-gapped… until someone brings a USB stick.",
    "In the logs, no one can hear you scream.",
    "The Architect prefers deterministic bugs.",
    "The most dangerous exploit sits at the keyboard.",
    "Wi-Fi with zero password, zero excuses.",
    "You had one job: change 'admin/admin'.",
    "In cyberspace, every click is a choice.",
    "The red pill is basically full disk encryption.",
    "There is always one more hidden menu.",
    "Your data wants a better bodyguard.",
    "Someone pasted secrets into a public repo.",
    "Incognito mode is not witness protection.",
    "The Matrix updates while you sleep.",
    "If it blinks, it can be hacked.",
    "Default SSID, default destiny.",
    "A honeypot is just a polite trap.",
    "Strong passphrase, weak coffee.",
    "The rabbit hole has better logging now.",
    "Agent Smith loves weak certificates.",
    "Entropy is a hacker’s favorite spice.",
    "Neo, your password has expired.",
    "Cypher chose steak over security.",
    "Free Wi-Fi usually costs your data.",
    "The keymaker just generates SSH keys now.",
    "A secure system is one no one uses.",
    "Your click-accept EULA sold your soul.",
    "There is no offline, only lag.",
    "The spoon was a buffer overflow.",
    "Every 'temp fix' lives forever in prod.",
    "Neo, your MFA code is 101010.",
    "The Matrix pings, you pong.",
    "You can't patch human curiosity.",
    "Zero-day, meet zero-backup.",
    "The rabbit uses end-to-end encryption.",
    "DNS is the phonebook of the Matrix.",
    "Someone left RDP open to the world.",
    "Password123 is not a lifestyle, it’s a breach.",
    "The simulation lags when you open too many tabs.",
    "There is no safe USB in the wild.",
    "The Operator sees every dropped packet.",
    "Your webcam light should not surprise you.",
    "The system admin is the true chosen one.",
    "Red team, blue team, same playground.",
    "Every port tells a small secret.",
    "QR codes can be rabbit holes too.",
    "The spoon is now a phishing link.",
    "Neo, your session has timed out.",
    "Incidents start with 'it’s probably nothing'.",
    "The Matrix runs on deprecated APIs.",
    "The black cat was just a failed ping.",
    "You had me at 'public exploit PoC'.",
    "Coffee in, logs out.",
    "Malware loves unpatched drivers.",
    "The rabbit’s IP address keeps changing.",
    "Even the Oracle checks Shodan.",
    "Your password leaked before your coffee cooled.",
    "The Matrix doesn’t crash, it 'reboots reality'.",
    "Never store secrets in screenshots.",
    "Neo, follow the log files, not the crowd.",
    "If you can’t find the bug, check the config.",
    "Every unsecured Wi-Fi is a story waiting to happen.",
    "Sometimes the most secure port is unplugged.",
    "The Architect prefers green text on black.",
    "You didn’t break the system, you found the edge."
]

def init_pygame():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)
    font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
    return screen, font


def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            pygame.quit()
            sys.exit()


def render_line(screen: pygame.Surface, font: pygame.font.Font, text: str, visible: int, show_cursor: bool = True):
    screen.fill(BLACK)
    visible_text = text[:visible]
    surf = font.render(visible_text, True, GREEN)
    screen.blit(surf, (LINE_X, LINE_Y))
    if show_cursor:
        size = font.get_height() - 4
        cx = LINE_X + surf.get_width() + 4
        cy = LINE_Y + 2
        pygame.draw.rect(screen, WHITE, (cx, cy, size, size))
    pygame.display.update()


def type_sentence(screen: pygame.Surface, font: pygame.font.Font, sentence: str) -> str:
    txt = ""
    for ch in sentence:
        handle_events()
        if ch != " " and random.random() < MISTAKE_PROBABILITY:
            wrong = random.choice(MISTAKE_CHARS)
            txt += wrong
            render_line(screen, font, txt, len(txt), True)
            pygame.time.delay(random.randint(MISTAKE_MIN_DELAY_MS, MISTAKE_MAX_DELAY_MS))
            txt = txt[:-1]
            render_line(screen, font, txt, len(txt), True)
            pygame.time.delay(random.randint(MISTAKE_MIN_DELAY_MS, MISTAKE_MAX_DELAY_MS))
        txt += ch
        render_line(screen, font, txt, len(txt), True)
        pygame.time.delay(random.randint(TYPE_MIN_DELAY_MS, TYPE_MAX_DELAY_MS))
    return txt


def delete_sentence(screen: pygame.Surface, font: pygame.font.Font, sentence: str):
    for i in range(len(sentence), -1, -1):
        handle_events()
        render_line(screen, font, sentence, i, True)
        pygame.time.delay(random.randint(MISTAKE_MIN_DELAY_MS, MISTAKE_MAX_DELAY_MS))


def blink_full(screen: pygame.Surface, font: pygame.font.Font, sentence: str):
    for _ in range(BLINK_COUNT):
        handle_events()
        render_line(screen, font, sentence, len(sentence), True)
        pygame.time.delay(BLINK_ON_MS)
        render_line(screen, font, sentence, len(sentence), False)
        pygame.time.delay(BLINK_OFF_MS)


def main():
    screen, font = init_pygame()
    random.shuffle(LINES)
    while True:
        for s in LINES:
            handle_events()
            typed = type_sentence(screen, font, s)
            pygame.time.delay(400)
            blink_full(screen, font, typed)
            pygame.time.delay(150)
            delete_sentence(screen, font, typed)
            pygame.time.delay(250)
        random.shuffle(LINES)


if __name__ == "__main__":
    try:
        main()
    finally:
        pygame.quit()
        sys.exit()
