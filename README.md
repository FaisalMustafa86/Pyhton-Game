# 🐱 Cat Invasion 🚀

Cat Invasion is a **2D space shooter** built with **Python + Pygame**.
Pilot a fighter jet and defend the skies from waves of invading cats — dodge
their fire, dash out of danger, and rack up the highest score you can.

A fast, juicy free-roam arena shooter: parallax starfield, particle explosions,
screen shake, escalating waves, boss cats, and a saved high score.

---

## 🎮 Features
- **Free-roam flight** — full 2D movement with a short-cooldown **dash**
- **Hold-to-fire** shooting with muzzle sparks and a thruster trail
- **Escalating waves** — more (and faster) cats every round
- **Multiple enemy types** — grunt cats, quick cats, and a **boss cat** every 5th wave (with spread-shot attacks)
- **Juice** — parallax starfield, explosion particles, screen shake, hit flashes, floating score pop-ups
- **Lives system** with brief invulnerability + respawn on hit
- **Polished UI** — animated menu, pause overlay, and a game-over screen
- **Persistent high score** (saved to `highscore.json`)
- **Procedural sound effects** + background music

---

## 🕹️ Controls
| Key | Action |
|-----|--------|
| **W A S D** / **Arrows** | Move |
| **L** / **Space** | Fire (hold) |
| **L-Shift** | Dash (while moving) |
| **P** | Pause / Resume |
| **Esc** | Pause · back to menu · quit from menu |
| **Mouse** | Menu buttons (Play, Retry, Menu, Quit) |

---

## 📂 Project Structure
```
Cat-Invasion/
│── Main.py       # Entry point (init + main loop)
│── game.py       # Game state machine, waves, collisions, scoring
│── settings.py   # All tunable constants
│── assets.py     # Image/font caching + procedural sound synthesis
│── player.py     # Player jet (movement, dash, firing)
│── enemy.py      # Cat enemies (grunt / fast / boss)
│── bullet.py     # Shared projectile for player & enemies
│── effects.py    # Starfield, particles, floating text, screen shake
│── ui.py         # Buttons, HUD, menu / pause / game-over screens
│── Assets/       # Images, sounds, music
└── README.md
```

---

## ▶️ How to Run
1. Install Python (3.10+ recommended).
2. Install **pygame**:
   ```bash
   pip install pygame
   ```
3. Run the game from the project folder:
   ```bash
   python Main.py
   ```

---

## 👨‍💻 Author
Made with ❤️ by Faisal
