#!/usr/bin/env python3
"""
Generate a retro terminal boot GIF for Kaan Turgut's GitHub profile.
Uses Pillow to create a dark-themed terminal animation frame by frame.
"""

import os
from PIL import Image, ImageDraw, ImageFont
import math

# --- Configuration ---
OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "terminal-boot.gif")
WIDTH = 800
HEIGHT = 520
CHAR_WIDTH = 9
CHAR_HEIGHT = 18
PADDING_X = 16
PADDING_Y = 12

# Gruvbox Dark theme
BG_COLOR = (40, 40, 40)          # #282828
FG_COLOR = (235, 219, 178)       # #ebdbb2
GREEN = (152, 151, 26)           # #98971a
BRIGHT_GREEN = (184, 187, 38)    # #b8bb26
AQUA = (104, 157, 106)           # #689d6a
BRIGHT_AQUA = (142, 192, 124)    # #8ec07c
YELLOW = (215, 153, 33)          # #d79921
BRIGHT_YELLOW = (250, 189, 47)   # #fabd2f
ORANGE = (214, 93, 14)           # #d65d0e
RED = (204, 36, 29)              # #cc241d
BLUE = (69, 133, 136)            # #458588
BRIGHT_BLUE = (131, 165, 152)    # #83a598
PURPLE = (177, 98, 134)          # #b16286
GRAY = (146, 131, 116)           # #928374
TITLE_BAR_BG = (29, 32, 33)     # #1d2021
CURSOR_COLOR = BRIGHT_GREEN

# Terminal title bar height
TITLE_BAR_HEIGHT = 28


def get_monospace_font(size=14):
    """Try to find a monospace font, fall back to default."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/SFMono-Regular.otf",
        "/System/Library/Fonts/Monaco.dfont",
        "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
        "/usr/share/fonts/dejavu/DejaVuSansMono.ttf",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    # Fallback
    try:
        return ImageFont.truetype("DejaVuSansMono.ttf", size)
    except Exception:
        return ImageFont.load_default()


def create_base_frame(font):
    """Create a base terminal frame with title bar."""
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Title bar background
    draw.rectangle([0, 0, WIDTH, TITLE_BAR_HEIGHT], fill=TITLE_BAR_BG)

    # Window control dots
    dot_y = TITLE_BAR_HEIGHT // 2
    for i, color in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        draw.ellipse([12 + i * 22, dot_y - 6, 12 + i * 22 + 12, dot_y + 6], fill=color)

    # Title text
    title = "kaan@cloud-infra.io: ~"
    try:
        title_font = get_monospace_font(12)
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
    except Exception:
        tw = len(title) * 7
        title_font = font
    draw.text(((WIDTH - tw) // 2, 6), title, fill=GRAY, font=title_font)

    return img


# --- Define the boot sequence lines ---
# Each entry: (text, color, delay_frames, is_typed)
# delay_frames = number of frames this line stays before next line appears
# is_typed = if True, animate character by character

BOOT_SEQUENCE = [
    # SSH connection
    ("$ ssh kaan@cloud-infra.io", BRIGHT_GREEN, 1, True),
    ("Connecting...", GRAY, 3, False),
    ("Connected to kaan@cloud-infra.io", BRIGHT_AQUA, 2, False),
    ("Last login: Sat Apr 11 09:42:17 2026 from 10.0.1.42", GRAY, 3, False),
    ("", None, 1, False),

    # whoami
    ("$ whoami", BRIGHT_GREEN, 1, True),
    ("> Kaan Turgut", BRIGHT_YELLOW, 1, False),
    ("> Lead DevOps Engineer | Cloud-Native Strategist", YELLOW, 3, False),
    ("", None, 1, False),

    # cat /etc/profile
    ("$ cat /etc/profile", BRIGHT_GREEN, 1, True),
    ("> Location:  Toronto, Canada", FG_COLOR, 1, False),
    ("> Company:   Lenovo", FG_COLOR, 1, False),
    ("> Focus:     AI-Powered DevOps, Cloud Architecture,", FG_COLOR, 1, False),
    (">            Agentic Workflows", FG_COLOR, 3, False),
    ("", None, 1, False),

    # kubectl get certifications
    ("$ kubectl get certifications", BRIGHT_GREEN, 1, True),
    ("NAME                               STATUS", BRIGHT_BLUE, 1, False),
    ("microsoft-ai-mvp                   Active", FG_COLOR, 1, False),
    ("azure-solutions-architect-expert   Active", FG_COLOR, 1, False),
    ("azure-ai-engineer-associate        Active", FG_COLOR, 3, False),
    ("", None, 1, False),

    # terraform plan
    ("$ terraform plan -out=connect", BRIGHT_GREEN, 1, True),
    ("", None, 1, False),
    ("Plan: LinkedIn, Medium, YouTube, Email", PURPLE, 1, False),
    ("", None, 1, False),
    ("Apply complete! Let's connect.", BRIGHT_GREEN, 8, False),
]


def render_lines_on_frame(base_img, font, lines_to_render, show_cursor=True, cursor_x_offset=None, cursor_line=None):
    """
    Render a list of (text, color) onto the terminal frame.
    Returns a new Image.
    """
    img = base_img.copy()
    draw = ImageDraw.Draw(img)

    y = TITLE_BAR_HEIGHT + PADDING_Y
    last_x = PADDING_X
    last_y = y

    for i, (text, color) in enumerate(lines_to_render):
        if text == "":
            y += CHAR_HEIGHT
            continue
        draw.text((PADDING_X, y), text, fill=color, font=font)
        # Track last line position for cursor
        try:
            bbox = draw.textbbox((PADDING_X, y), text, font=font)
            last_x = bbox[2] + 2
        except Exception:
            last_x = PADDING_X + len(text) * CHAR_WIDTH + 2
        last_y = y
        y += CHAR_HEIGHT

    # Cursor
    if show_cursor:
        if cursor_x_offset is not None and cursor_line is not None:
            cx = cursor_x_offset
            cy = cursor_line
        else:
            cx = last_x
            cy = last_y
        draw.rectangle([cx, cy, cx + CHAR_WIDTH, cy + CHAR_HEIGHT - 2], fill=CURSOR_COLOR)

    return img


def generate_gif():
    font = get_monospace_font(14)
    base = create_base_frame(font)

    frames = []
    durations = []  # in ms

    # Start with empty terminal + blinking cursor (a few frames)
    y_start = TITLE_BAR_HEIGHT + PADDING_Y
    for blink in range(4):
        show = blink % 2 == 0
        f = render_lines_on_frame(base, font, [], show_cursor=show,
                                  cursor_x_offset=PADDING_X, cursor_line=y_start)
        frames.append(f)
        durations.append(300)

    rendered_lines = []  # list of (text, color) already shown

    for text, color, delay, is_typed in BOOT_SEQUENCE:
        if text == "":
            rendered_lines.append(("", FG_COLOR))
            f = render_lines_on_frame(base, font, rendered_lines)
            frames.append(f)
            durations.append(80)
            continue

        if is_typed:
            # Type out character by character
            for ci in range(1, len(text) + 1):
                partial = text[:ci]
                temp_lines = rendered_lines + [(partial, color)]
                f = render_lines_on_frame(base, font, temp_lines)
                frames.append(f)
                durations.append(35)  # typing speed
            # Pause after full typed line
            rendered_lines.append((text, color))
            f = render_lines_on_frame(base, font, rendered_lines)
            frames.append(f)
            durations.append(200)
        else:
            # Instant appear
            rendered_lines.append((text, color))
            f = render_lines_on_frame(base, font, rendered_lines)
            frames.append(f)
            durations.append(120)

        # Extra delay frames (hold)
        if delay > 1:
            for _ in range(delay - 1):
                f = render_lines_on_frame(base, font, rendered_lines)
                frames.append(f)
                durations.append(150)

    # Final frames: blink cursor a few times at the end
    for blink in range(8):
        show = blink % 2 == 0
        f = render_lines_on_frame(base, font, rendered_lines, show_cursor=show)
        frames.append(f)
        durations.append(400)

    # Save GIF
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    frames[0].save(
        OUTPUT_PATH,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )
    print(f"GIF saved to {OUTPUT_PATH}")
    print(f"Frames: {len(frames)}")
    file_size = os.path.getsize(OUTPUT_PATH)
    print(f"File size: {file_size / 1024:.1f} KB")


if __name__ == "__main__":
    generate_gif()
