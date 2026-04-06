#!/usr/bin/env python3
"""
Auto-generate catalog.json by scanning ALL sound folders.
- Scans every subfolder (except hidden/system) for .mp3 files
- Preserves existing entries (name, iconName, isLocked) from current catalog
- New files get isLocked=false, isNew=true
- New folders auto-create a category entry
"""

import json
import os
from pathlib import Path

REPO_URL = "https://raw.githubusercontent.com/huytrandevgit/serenityscape-sounds/main"

# Folders to skip
SKIP_FOLDERS = {".git", ".github", "__pycache__", ".DS_Store", "node_modules"}

# Default icons and colors per known category
KNOWN_CATEGORIES = {
    "nature": {"title": "Nature Sounds", "subtitle": "Relax with nature", "icon": "leaf.fill", "colors": ["#33D96B", "#00BCD4"]},
    "baby_sleep": {"title": "Baby Sleep", "subtitle": "Gentle lullabies", "icon": "moon.zzz.fill", "colors": ["#9B59B6", "#3F51B5"]},
    "meditation_hz": {"title": "Healing Frequencies", "subtitle": "Sound healing", "icon": "waveform.path", "colors": ["#FF9800", "#FFEB3B"]},
    "meditation_music": {"title": "Zen & Yoga", "subtitle": "Meditation & yoga music", "icon": "sparkles", "colors": ["#E91E63", "#9B59B6"]},
}

# Fallback colors for new categories
NEW_CATEGORY_COLORS = [
    ["#00BCD4", "#2196F3"],  # teal-blue
    ["#FF6B6B", "#EE5A24"],  # red-orange
    ["#A29BFE", "#6C5CE7"],  # lavender-purple
    ["#FDCB6E", "#F39C12"],  # gold-amber
    ["#00CEC9", "#0984E3"],  # cyan-blue
    ["#E17055", "#D63031"],  # coral-red
]

# Default SF Symbol icons for new categories
DEFAULT_ICON = "music.note"


def load_existing_catalog(path: str) -> tuple:
    """Load existing catalog.json. Returns (sounds_dict, categories_dict, version)."""
    if not os.path.exists(path):
        return {}, {}, 1
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    sounds = {s["fileName"]: s for s in data.get("sounds", [])}
    cats = {c["id"]: c for c in data.get("categories", [])}
    return sounds, cats, data.get("version", 1)


def discover_folders(root: str) -> list:
    """Find all subfolders containing .mp3 files."""
    folders = []
    for entry in sorted(Path(root).iterdir()):
        if not entry.is_dir():
            continue
        if entry.name in SKIP_FOLDERS or entry.name.startswith("."):
            continue
        mp3s = list(entry.glob("*.mp3"))
        if mp3s:
            folders.append(entry.name)
    return folders


def make_display_name(file_name: str) -> str:
    """Convert file_name to display name."""
    clean = file_name
    for prefix in ["baby_", "med_", "hz_"]:
        if clean.lower().startswith(prefix):
            clean = clean[len(prefix):]
            break
    return clean.replace("_", " ").upper()


def make_icon_name(file_name: str) -> str:
    """Map filename to a valid SF Symbol icon name based on keywords."""
    name = file_name.lower()
    
    # Keyword-based icon mapping
    keyword_icons = {
        "ocean": "water.waves",
        "rain": "cloud.rain.fill",
        "thunder": "cloud.bolt.fill",
        "wind": "wind",
        "fire": "flame.fill",
        "campfire": "flame.fill",
        "bird": "bird.fill",
        "forest": "tree.fill",
        "leaf": "leaf.fill",
        "stream": "water.waves",
        "wave": "water.waves",
        "piano": "pianokeys",
        "guitar": "guitars.fill",
        "flute": "music.note",
        "drum": "circle.grid.3x3.fill",
        "bowl": "circle.hexagongrid.fill",
        "bell": "bell.fill",
        "chant": "person.fill",
        "choir": "person.3.fill",
        "heart": "heart.fill",
        "sleep": "moon.zzz.fill",
        "dream": "cloud.fill",
        "night": "moon.stars.fill",
        "morning": "sunrise.fill",
        "sun": "sun.max.fill",
        "star": "star.fill",
        "peace": "leaf.circle.fill",
        "calm": "wind",
        "zen": "sparkles",
        "yoga": "figure.mind.and.body",
        "meditat": "brain.head.profile",
        "heal": "staroflife.fill",
        "crystal": "sparkles",
        "temple": "building.columns.fill",
        "gong": "circle.fill",
        "harp": "music.quarternote.3",
        "sitar": "guitars.fill",
        "bamboo": "leaf.fill",
        "cave": "mountain.2.fill",
        "mountain": "mountain.2.circle.fill",
        "desert": "sun.max.fill",
        "snow": "snowflake",
        "ice": "snowflake",
        "whale": "fish.fill",
        "frog": "tortoise.fill",
        "cricket": "ant.fill",
        "baby": "moon.stars.fill",
        "lullaby": "moon.stars.fill",
        "white_noise": "waveform",
        "fan": "fan.fill",
        "vacuum": "circle.dotted",
        "gentle": "leaf.fill",
        "soft": "cloud.fill",
        "deep": "waveform.path",
        "alpha": "brain.head.profile",
        "theta": "moon.zzz.fill",
        "delta": "bed.double.fill",
        "gamma": "bolt.fill",
        "hz": "waveform.path",
        "binaural": "waveform",
        "om": "circle.circle.fill",
        "mantra": "water.waves",
        "sacred": "person.3.fill",
        "space": "moon.stars.fill",
        "ambient": "waveform",
        "relax": "leaf.circle.fill",
        "breeze": "wind",
        "spring": "bird.fill",
        "autumn": "leaf.fill",
        "summer": "sun.max.fill",
        "winter": "snowflake",
        "river": "water.waves",
        "lake": "drop.degreesign.fill",
        "waterfall": "drop.triangle.fill",
        "recharge": "bolt.fill",
        "energy": "bolt.fill",
        "focus": "brain.head.profile",
        "study": "book.fill",
        "read": "book.fill",
        "work": "desktopcomputer",
        "lofi": "headphones",
        "chill": "cup.and.saucer.fill",
        "coffee": "cup.and.saucer.fill",
        "tropical": "cloud.heavyrain.fill",
        "island": "moon.stars.fill",
        "country": "sun.and.horizon.fill",
        "horse": "figure.equestrian.sports",
        "sheep": "pawprint.fill",
        "duck": "bird.fill",
    }
    
    for keyword, icon in keyword_icons.items():
        if keyword in name:
            return icon
    
    # Fallback: rotate through pleasant icons
    import hashlib
    fallback_icons = [
        "music.note", "sparkles", "star.fill", "heart.fill",
        "leaf.fill", "moon.stars.fill", "waveform.path", "wind",
        "cloud.fill", "drop.fill", "flame.fill", "circle.hexagongrid.fill",
    ]
    h = int(hashlib.md5(name.encode()).hexdigest(), 16)
    return fallback_icons[h % len(fallback_icons)]


def folder_to_title(folder_name: str) -> str:
    """Convert folder name to display title: 'focus_music' -> 'Focus Music'."""
    return folder_name.replace("_", " ").title()


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    catalog_path = os.path.join(root, "catalog.json")

    existing_sounds, existing_cats, old_version = load_existing_catalog(catalog_path)

    # Discover all folders with mp3s
    folders = discover_folders(root)
    print(f"📁 Found folders: {folders}")

    # Build categories
    categories = []
    color_idx = 0
    for folder in folders:
        cat_id = folder.lower()
        if cat_id in existing_cats:
            categories.append(existing_cats[cat_id])
        elif cat_id in KNOWN_CATEGORIES:
            info = KNOWN_CATEGORIES[cat_id]
            categories.append({
                "id": cat_id,
                "title": info["title"],
                "subtitle": info["subtitle"],
                "iconName": info["icon"],
                "colors": info["colors"],
            })
        else:
            # New category — auto-generate
            colors = NEW_CATEGORY_COLORS[color_idx % len(NEW_CATEGORY_COLORS)]
            color_idx += 1
            cat_entry = {
                "id": cat_id,
                "title": folder_to_title(folder),
                "subtitle": f"Explore {folder_to_title(folder).lower()}",
                "iconName": DEFAULT_ICON,
                "colors": colors,
            }
            categories.append(cat_entry)
            print(f"  + NEW CATEGORY: {cat_entry['title']}")

    # Scan sounds
    sounds = []
    new_count = 0
    for folder in folders:
        cat_id = folder.lower()
        folder_path = Path(root) / folder
        for mp3 in sorted(folder_path.glob("*.mp3")):
            fn = mp3.stem
            url = f"{REPO_URL}/{folder}/{mp3.name}"

            if fn in existing_sounds:
                entry = existing_sounds[fn].copy()
                entry["url"] = url
                sounds.append(entry)
            else:
                entry = {
                    "name": make_display_name(fn),
                    "fileName": fn,
                    "iconName": make_icon_name(fn),
                    "category": cat_id,
                    "isLocked": False,
                    "isNew": True,
                    "url": url,
                }
                sounds.append(entry)
                new_count += 1
                print(f"  + NEW SOUND: {entry['name']} ({cat_id})")

    version = old_version + 1 if new_count > 0 else old_version

    catalog = {
        "version": version,
        "categories": categories,
        "sounds": sounds,
    }

    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    print(f"\n✅ catalog.json: {len(sounds)} sounds, {len(categories)} categories, {new_count} new, v{version}")


if __name__ == "__main__":
    main()
