from pathlib import Path

# Root frontend folder
frontend_root = Path("frontend/src/app")

# Map of mojibake -> correct UTF-8 characters
replacements = {
    "âœ“": "✓",   # check mark
    "âœ—": "✗",   # cross mark
    "â€”": "—",   # em-dash
    "â€“": "–",   # en-dash
    "ðŸ”’": "→",  # right arrow
    "ðŸ“Š": "←",  # left arrow
    "âš": "⚠",    # warning
    "â€¦": "…",   # ellipsis
    "â‚¹": "₹",   # rupee
    "â—": "●",
    "â—‹": "○",
    "â–²": "▲",
    "â–¼": "▼",
    "â–¶": "▶",
    "â– ": "■",
    "âš¡": "⚡",
}

# Find all TypeScript files in frontend recursively
ts_files = list(frontend_root.rglob("*.ts"))

print(f"Scanning {len(ts_files)} TypeScript files...\n")

for file in ts_files:
    try:
        text = file.read_text(encoding="utf-8")
        modified = text
        for old, new in replacements.items():
            modified = modified.replace(old, new)
        if modified != text:
            file.write_text(modified, encoding="utf-8")
            print(f"Fixed: {file}")
        else:
            print(f"Clean: {file}")
    except Exception as e:
        print(f"Error processing {file}: {e}")

print("\nFrontend TS encoding repair finished!")
