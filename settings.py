"""Central configuration for Cat Invasion.

All tunable constants live here so gameplay can be balanced in one place.
"""

# --- Display -----------------------------------------------------------------
WIDTH = 900
HEIGHT = 600
FPS = 60
TITLE = "Cat Invasion"

# Play area: the player is free to roam, but cats keep some distance from the
# very bottom so the fight stays readable.
PLAY_TOP = 0
PLAY_BOTTOM = HEIGHT

# --- Colors ------------------------------------------------------------------
BLACK = (0, 0, 0)
WHITE = (245, 245, 255)
SPACE_TOP = (10, 8, 28)          # deep space gradient (top)
SPACE_BOTTOM = (28, 16, 46)      # deep space gradient (bottom)
UI_ACCENT = (120, 220, 255)      # cyan HUD accent
UI_ACCENT_DIM = (60, 120, 150)
UI_WARN = (255, 90, 120)         # pink/red for lives & danger
UI_GOOD = (150, 255, 170)
PLAYER_TINT = (150, 220, 255)
CAT_TINT = (255, 200, 120)
GOLD = (255, 210, 90)

# --- Player ------------------------------------------------------------------
PLAYER_SCALE = 2.0
PLAYER_SPEED = 5.0
PLAYER_DASH_SPEED = 14.0
PLAYER_DASH_DURATION = 180        # ms the dash impulse lasts
PLAYER_DASH_COOLDOWN = 700        # ms before the player can dash again
PLAYER_FIRE_COOLDOWN = 220        # ms between shots (hold to fire)
PLAYER_LIVES = 3
PLAYER_INVULN_TIME = 1500         # ms of i-frames after respawn / hit

# --- Bullets -----------------------------------------------------------------
PLAYER_BULLET_SPEED = 12.0
ENEMY_BULLET_SPEED = 6.0

# --- Enemies -----------------------------------------------------------------
ENEMY_BASE_SPEED = 2.2
ENEMY_FIRE_COOLDOWN = 1400        # ms baseline; scaled down as waves progress

# --- Waves -------------------------------------------------------------------
WAVE_BASE_COUNT = 3               # cats in wave 1
WAVE_COUNT_GROWTH = 1             # extra cats per wave
WAVE_MAX_ONSCREEN = 10            # cap simultaneous cats
BOSS_EVERY = 5                    # a boss cat appears on every Nth wave

# --- Scoring -----------------------------------------------------------------
SCORE_GRUNT = 10
SCORE_FAST = 20
SCORE_BOSS = 150

# --- Files -------------------------------------------------------------------
HIGHSCORE_FILE = "highscore.json"

# --- Game states -------------------------------------------------------------
STATE_MENU = "menu"
STATE_PLAY = "play"
STATE_PAUSE = "pause"
STATE_GAMEOVER = "gameover"
