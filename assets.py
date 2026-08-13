"""Asset loading and caching for Cat Invasion.

Images are loaded once and converted for fast blitting. Fonts fall back
gracefully when a preferred family is unavailable. Sound effects are
synthesized at runtime (no numpy dependency) so the game feels punchy even
though only a couple of audio files ship with the project.
"""

import array
import math
import os

import pygame

ASSET_DIR = "Assets"

_images = {}
_fonts = {}
_sounds = {}

# Fonts we would like, in order of preference. Falls back to pygame's default.
_PREFERRED_FONTS = [
    "pressstart2p", "vt323", "sharetechmono", "jetbrainsmono",
    "dejavusansmono", "firacode", "hack", "consolas", "liberationmono",
    "ubuntumono", "couriernew",
]
_FONT_NAME = None


def _path(name):
    return os.path.join(ASSET_DIR, name)


# --- Images ------------------------------------------------------------------
def load_image(name, scale=1.0, size=None, rotate=0, flip=False):
    """Load (and cache) an image, optionally scaled/sized/rotated/flipped."""
    key = (name, scale, size, rotate, flip)
    if key in _images:
        return _images[key]

    img = pygame.image.load(_path(name)).convert_alpha()
    if size is not None:
        img = pygame.transform.smoothscale(img, size)
    elif scale != 1.0:
        w, h = img.get_size()
        img = pygame.transform.smoothscale(img, (max(1, int(w * scale)),
                                                 max(1, int(h * scale))))
    if flip:
        img = pygame.transform.flip(img, False, True)
    if rotate:
        img = pygame.transform.rotate(img, rotate)

    _images[key] = img
    return img


def tinted_copy(surface, color, alpha=255):
    """Return a white-hot flash copy of a sprite (used for hit feedback)."""
    flash = surface.copy()
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((*color, alpha))
    flash.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    # Re-apply the sprite's own alpha mask so only opaque pixels flash.
    result = surface.copy()
    result.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return result


# --- Fonts -------------------------------------------------------------------
def _resolve_font_name():
    global _FONT_NAME
    if _FONT_NAME is not None:
        return _FONT_NAME
    available = set(pygame.font.get_fonts())
    for name in _PREFERRED_FONTS:
        if name in available:
            _FONT_NAME = name
            break
    else:
        _FONT_NAME = ""  # pygame default
    return _FONT_NAME


def font(size, bold=True):
    key = (size, bold)
    if key not in _fonts:
        name = _resolve_font_name()
        _fonts[key] = pygame.font.SysFont(name, size, bold=bold)
    return _fonts[key]


# --- Sound synthesis ---------------------------------------------------------
_SAMPLE_RATE = 44100


def _make_sound(samples):
    """Build a stereo pygame Sound from a list of mono floats in [-1, 1]."""
    buf = array.array("h")
    for s in samples:
        v = int(max(-1.0, min(1.0, s)) * 32767)
        buf.append(v)  # left
        buf.append(v)  # right
    return pygame.mixer.Sound(buffer=buf.tobytes())


def _tone(freq_start, freq_end, dur, vol=0.5, kind="sine", decay=True):
    n = int(_SAMPLE_RATE * dur)
    out = []
    for i in range(n):
        t = i / n
        freq = freq_start + (freq_end - freq_start) * t
        phase = 2 * math.pi * freq * (i / _SAMPLE_RATE)
        if kind == "square":
            wave = 1.0 if math.sin(phase) >= 0 else -1.0
        elif kind == "saw":
            wave = 2.0 * ((freq * i / _SAMPLE_RATE) % 1.0) - 1.0
        else:
            wave = math.sin(phase)
        env = (1.0 - t) if decay else 1.0
        out.append(wave * vol * env)
    return out


def _noise(dur, vol=0.5, decay=True):
    import random
    n = int(_SAMPLE_RATE * dur)
    out = []
    for i in range(n):
        t = i / n
        env = (1.0 - t) if decay else 1.0
        out.append((random.random() * 2 - 1) * vol * env)
    return out


def _mix(*layers):
    length = max(len(l) for l in layers)
    out = [0.0] * length
    for layer in layers:
        for i, v in enumerate(layer):
            out[i] += v
    return out


def _build_sfx():
    """Synthesize all sound effects once at startup."""
    try:
        _sounds["shoot"] = _make_sound(_tone(880, 320, 0.10, vol=0.25, kind="square"))
        _sounds["enemy_shoot"] = _make_sound(_tone(260, 140, 0.14, vol=0.18, kind="saw"))
        _sounds["hit"] = _make_sound(_tone(600, 200, 0.08, vol=0.3, kind="square"))
        _sounds["explosion"] = _make_sound(
            _mix(_noise(0.35, vol=0.4), _tone(200, 40, 0.35, vol=0.3, kind="saw")))
        _sounds["player_hit"] = _make_sound(
            _mix(_noise(0.5, vol=0.45), _tone(160, 30, 0.5, vol=0.4, kind="square")))
        _sounds["wave"] = _make_sound(
            _mix(_tone(440, 660, 0.18, vol=0.25, kind="sine", decay=False),
                 _tone(660, 880, 0.18, vol=0.2, kind="sine", decay=False)))
        _sounds["ui"] = _make_sound(_tone(520, 760, 0.06, vol=0.25, kind="square"))
        _sounds["gameover"] = _make_sound(_tone(400, 90, 0.7, vol=0.35, kind="saw"))
    except Exception as exc:  # never let audio kill the game
        print(f"[assets] sound synthesis failed: {exc}")


def load_all_sounds():
    """Load music + synthesize SFX. Safe to call once the mixer is ready."""
    _build_sfx()


def play(name, volume=1.0):
    snd = _sounds.get(name)
    if snd is not None:
        snd.set_volume(volume)
        snd.play()


def play_music(volume=0.4):
    try:
        pygame.mixer.music.load(_path("bgMusic.mp3"))
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)
    except Exception as exc:
        print(f"[assets] music failed to load: {exc}")
