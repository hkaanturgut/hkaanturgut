"""Update the guestbook section in README.md from a GitHub issue."""

import os
import re
from datetime import datetime, timezone


def main():
    title = os.environ["ISSUE_TITLE"]
    author = os.environ["ISSUE_AUTHOR"]
    issue_number = os.environ["ISSUE_NUMBER"]

    # Extract message after "Guestbook:" prefix
    message = title.split("Guestbook:", 1)[1].strip()
    if not message:
        print("Empty guestbook message, skipping.")
        return

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    new_row = f"| @{author} | {message} | {today} |"

    readme_path = "README.md"
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    start_marker = "<!-- GUESTBOOK:START -->"
    end_marker = "<!-- GUESTBOOK:END -->"

    pattern = re.compile(
        rf"({re.escape(start_marker)})\n(.*?)(\n{re.escape(end_marker)})",
        re.DOTALL,
    )

    match = pattern.search(content)
    if not match:
        print(f"Could not find guestbook markers in {readme_path}")
        return

    existing_block = match.group(2).strip()

    # Parse existing rows (skip empty lines and the table header/separator)
    rows = []
    for line in existing_block.splitlines():
        stripped = line.strip()
        # Keep only data rows (start with | @ )
        if stripped.startswith("| @"):
            rows.append(stripped)

    # Prepend the new entry and keep only the latest 10
    rows.insert(0, new_row)
    rows = rows[:10]

    table_header = "| Name | Message | Date |\n|------|---------|------|"
    new_block = table_header + "\n" + "\n".join(rows)

    replacement = f"{start_marker}\n{new_block}\n{end_marker}"
    content = pattern.sub(replacement, content)

    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Guestbook updated with entry from @{author} (issue #{issue_number})")


if __name__ == "__main__":
    main()
