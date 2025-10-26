import json
from datetime import datetime
from pathlib import Path

SAVE_PATH = Path(r"C:\Users\lod19\OneDrive\Desktop\Python Playground\Beginners Projects\groceries.json")

def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def load():
    if SAVE_PATH.exists():
        try:
            with open(SAVE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    else:
        data = {}
    groceries = data.get("groceries", [])
    last_updated = data.get("last_updated", "Never")
    return groceries, last_updated

def save(groceries):
    data = {"groceries": groceries, "last_updated": timestamp()}
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"(Saved to: {SAVE_PATH})")

groceries, last_updated = load()

if not SAVE_PATH.exists():
    save(groceries)

print("Welcome to your Grocery List App! 🛍️")
print(f"Last updated: {last_updated}")
print(f"Data file: {SAVE_PATH}")

while True:
    select = input(
        "\n1. View list\n2. Add item\n3. Remove item\n4. Exit\nChoose an option: "
    ).strip()

    if select == "1":
        if groceries:
            print("\nYour grocery list:")
            for item in sorted(groceries):
                print("-", item.title())
        else:
            print("\nYour list is empty.")

    elif select == "2":
        item = input("Enter item to add: ").strip().lower()
        if item and item not in groceries:
            groceries.append(item)
            print(f"{item.title()} added to your list.")
            save(groceries)
        elif item:
            print(f"{item.title()} is already on your list.")

    elif select == "3":
        item = input("Enter item to remove: ").strip().lower()
        if item in groceries:
            groceries.remove(item)
            print(f"{item.title()} removed from your list.")
            save(groceries)
        else:
            print(f"{item.title()} is not in your list.")

    elif select == "4":
        save(groceries)
        print("Saved. Goodbye!")
        break

    else:
        print("Invalid option. Please try again.")
