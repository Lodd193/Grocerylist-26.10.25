import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).resolve().parent
SAVE_PATH = SCRIPT_DIR / "groceries.json"

# ---------------------------
# Data model
# items are dicts:
#   {"name": "milk", "category": "dairy", "bought": False}
# ---------------------------

TEMPLATES = {
    "Weekly Essentials": [
        {"name": "milk", "category": "dairy"},
        {"name": "bread", "category": "bakery"},
        {"name": "eggs", "category": "dairy"},
        {"name": "bananas", "category": "produce"},
    ],
    "BBQ Night": [
        {"name": "burgers", "category": "meat"},
        {"name": "burger buns", "category": "bakery"},
        {"name": "lettuce", "category": "produce"},
        {"name": "tomatoes", "category": "produce"},
    ],
    "Pasta Dinner": [
        {"name": "pasta", "category": "dry goods"},
        {"name": "passata", "category": "tins & jars"},
        {"name": "parmesan", "category": "dairy"},
        {"name": "basil", "category": "produce"},
    ],
}

def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def _normalise_name(s: str) -> str:
    return s.strip().lower()

def _normalise_category(s: str) -> str:
    s = s.strip().lower()
    return s if s else "uncategorised"

def _make_item(name: str, category: str = "", bought: bool = False) -> dict:
    return {
        "name": _normalise_name(name),
        "category": _normalise_category(category),
        "bought": bool(bought),
    }

def _ensure_model(item) -> dict:
    """Ensure any loaded entry matches our dict model (backward compatible)."""
    if isinstance(item, str):
        return _make_item(item)
    # guard for missing keys
    return {
        "name": _normalise_name(item.get("name", "")),
        "category": _normalise_category(item.get("category", "")),
        "bought": bool(item.get("bought", False)),
    }

def load():
    if SAVE_PATH.exists():
        try:
            with open(SAVE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    else:
        data = {}
    raw = data.get("groceries", [])
    groceries = [_ensure_model(x) for x in raw if isinstance(x, (str, dict))]
    last_updated = data.get("last_updated", "Never")
    return groceries, last_updated

def save(groceries):
    data = {"groceries": groceries, "last_updated": timestamp()}
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"(Saved to: {SAVE_PATH})")

def clear_list(groceries):
    confirm = input("Are you sure you want to clear the entire list? (yes/no): ").lower()
    if confirm == "yes":
        groceries.clear()
        save(groceries)
        print("All items have been removed from your list.")
    else:
        print("Clear list cancelled.")

def _find_index(groceries, name: str):
    name = _normalise_name(name)
    for i, it in enumerate(groceries):
        if it["name"] == name:
            return i
    return None

def _format_name(s: str) -> str:
    # Title case that keeps small words nice (simple approach)
    return s.title()

def display_list(groceries):
    if not groceries:
        print("\nYour list is empty.")
        return

    # Group by category, show pending first then bought
    groups = defaultdict(list)
    for it in groceries:
        groups[it["category"]].append(it)

    print("\nYour grocery list (grouped by category):")
    for category in sorted(groups.keys()):
        print(f"\n{category.capitalize()}:")
        # sort: bought last within category, then by name
        items_sorted = sorted(groups[category], key=lambda x: (x["bought"], x["name"]))
        for it in items_sorted:
            tick = "[x]" if it["bought"] else "[ ]"
            print(f" - {tick} {_format_name(it['name'])}")

def add_item(groceries):
    name = _normalise_name(input("Enter item to add: ").strip())
    if not name:
        print("No item entered.")
        return

    idx = _find_index(groceries, name)
    if idx is not None:
        print(f"{_format_name(name)} is already on your list.")
        return

    category = input("Category (optional, e.g., dairy, bakery, produce): ").strip()
    item = _make_item(name, category, bought=False)
    groceries.append(item)
    print(f"{_format_name(name)} added to your list.")
    save(groceries)

def remove_item(groceries):
    name = _normalise_name(input("Enter item to remove: ").strip())
    idx = _find_index(groceries, name)
    if idx is None:
        print(f"{_format_name(name)} is not in your list.")
        return
    removed = groceries.pop(idx)
    print(f"{_format_name(removed['name'])} removed from your list.")
    save(groceries)

def toggle_bought(groceries):
    name = _normalise_name(input("Enter item to toggle bought status: ").strip())
    idx = _find_index(groceries, name)
    if idx is None:
        print(f"{_format_name(name)} is not in your list.")
        return
    groceries[idx]["bought"] = not groceries[idx]["bought"]
    state = "bought" if groceries[idx]["bought"] else "not bought"
    print(f"{_format_name(name)} marked as {state}.")
    save(groceries)

def quick_add_templates(groceries):
    if not TEMPLATES:
        print("No templates available.")
        return

    print("\nQuick Add Templates:")
    keys = list(TEMPLATES.keys())
    for i, tname in enumerate(keys, start=1):
        # preview a few items
        items_preview = ", ".join(_format_name(x["name"]) for x in TEMPLATES[tname][:3])
        if len(TEMPLATES[tname]) > 3:
            items_preview += ", ..."
        print(f"{i}. {tname} ({items_preview})")

    choice = input("Select a template number (or press Enter to cancel): ").strip()
    if not choice:
        print("Cancelled.")
        return

    if not choice.isdigit() or not (1 <= int(choice) <= len(keys)):
        print("Invalid choice.")
        return

    selected = keys[int(choice) - 1]
    added = 0
    for entry in TEMPLATES[selected]:
        name = _normalise_name(entry.get("name", ""))
        if not name:
            continue
        if _find_index(groceries, name) is None:
            groceries.append(_make_item(name, entry.get("category", ""), bought=False))
            added += 1
    save(groceries)
    print(f"Added {added} new item(s) from '{selected}'. (Existing items were skipped.)")

def migrate_if_needed(groceries):
    """If any items are strings, migrate them to dicts."""
    changed = False
    for i in range(len(groceries)):
        if isinstance(groceries[i], str):
            groceries[i] = _ensure_model(groceries[i])
            changed = True
        else:
            # ensure keys exist
            if not all(k in groceries[i] for k in ("name", "category", "bought")):
                groceries[i] = _ensure_model(groceries[i])
                changed = True
    if changed:
        save(groceries)

# ---------------------------
# Main
# ---------------------------
groceries, last_updated = load()
migrate_if_needed(groceries)

if not SAVE_PATH.exists():
    save(groceries)

print("Welcome to your Grocery List App! 🛍️")
print(f"Last updated: {last_updated}")
print(f"Data file: {SAVE_PATH}")

while True:
    select = input(
        "\n1. View list"
        "\n2. Add item"
        "\n3. Remove item"
        "\n4. Clear list"
        "\n5. Toggle bought"
        "\n6. Quick add (templates)"
        "\n7. Exit"
        "\nChoose an option: "
    ).strip()

    if select == "1":
        display_list(groceries)

    elif select == "2":
        add_item(groceries)

    elif select == "3":
        remove_item(groceries)

    elif select == "4":
        clear_list(groceries)

    elif select == "5":
        toggle_bought(groceries)

    elif select == "6":
        quick_add_templates(groceries)

    elif select == "7":
        save(groceries)
        print("Saved. Goodbye!")
        break

    else:
        print("Invalid option. Please try again.")
