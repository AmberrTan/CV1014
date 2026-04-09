"""Console UI helpers for the gym recommendation system."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

from gym_recommender.data import generate_next_gym_id, save_database
from gym_recommender.models import GymRecord, SearchFilters
from gym_recommender.search import calculate_distance, search_gyms, sort_gyms

InputFn = Callable[[str], str]


def prompt_non_empty(prompt: str, input_fn: InputFn = input) -> str:
    """Prompt until the user provides a non-empty response."""
    while True:
        value = input_fn(prompt).strip()
        if value:
            return value
        print("Please enter a value.")


def prompt_keep_or_non_empty(current: str, prompt: str, input_fn: InputFn = input) -> str:
    """Prompt until a new or existing value is available."""
    while True:
        value = input_fn(prompt).strip()
        if value:
            return value
        if current:
            return current
        print("Please enter a value.")


def prompt_optional_float(prompt: str, input_fn: InputFn = input) -> float | None:
    """Prompt for a float value or return None if blank."""
    while True:
        value = input_fn(prompt).strip()
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            print("Please enter a valid number.")


def prompt_optional_int(prompt: str, input_fn: InputFn = input) -> int | None:
    """Prompt for an integer value or return None if blank."""
    while True:
        value = input_fn(prompt).strip()
        if not value:
            return None
        if value.isdigit():
            return int(value)
        print("Please enter a valid whole number.")


def prompt_yes_no(prompt: str, input_fn: InputFn = input, allow_blank: bool = True) -> bool | None:
    """Prompt for a Y/N answer, optionally allowing blank."""
    while True:
        value = input_fn(prompt).strip().lower()
        if allow_blank and not value:
            return None
        if value in {"y", "yes"}:
            return True
        if value in {"n", "no"}:
            return False
        print("Please enter Y/N or leave blank.")


def prompt_list(prompt: str, input_fn: InputFn = input) -> list[str]:
    """Prompt for a comma-separated list with de-duplication."""
    value = input_fn(prompt).strip()
    if not value:
        return []
    unique_items: list[str] = []
    seen: set[str] = set()
    for item in value.split(","):
        cleaned = item.strip()
        lowered = cleaned.casefold()
        if cleaned and lowered not in seen:
            unique_items.append(cleaned)
            seen.add(lowered)
    return unique_items


def format_time(value: int, is_24_hours: bool) -> str:
    """Format HHMM integer as a display string."""
    if is_24_hours:
        return "24 hours"
    hours = value // 100
    minutes = value % 100
    return f"{hours:02d}:{minutes:02d}"


def gym_summary_line(gym: GymRecord) -> str:
    """Return a one-line summary used in list displays."""
    hours = (
        "24 hours"
        if gym["is_24_hours"]
        else f"{format_time(gym['opening_time'], False)}-{format_time(gym['closing_time'], False)}"
    )
    facilities = ", ".join(gym["facilities"][:4])
    return (
        f"[{gym['gym_id']}] {gym['gym_name']} | {gym['area']} | "
        f"${gym['monthly_price']:.2f}/month | Rating {gym['rating']:.1f} | "
        f"{gym['gym_type']} | {hours} | {facilities}"
    )


def display_gyms(
    gyms: list[GymRecord],
    user_x: int | None = None,
    user_y: int | None = None,
) -> None:
    """Pretty-print a list of gyms with optional distance info."""
    if not gyms:
        print("No gyms found.")
        return
    for gym in gyms:
        print(gym_summary_line(gym))
        if user_x is not None and user_y is not None:
            distance = calculate_distance(user_x, user_y, gym["x_coordinate"], gym["y_coordinate"])
            print(f"  Distance score input: {distance:.2f} units away")
        print(f"  Address: {gym['address']}")
        print(f"  Facilities: {', '.join(gym['facilities'])}")
        print()


def display_all_gyms(gyms: list[GymRecord]) -> None:
    """Print every gym in the dataset."""
    print("\nAll gyms in the database:\n")
    display_gyms(gyms)


def get_search_filters(input_fn: InputFn = input) -> SearchFilters:
    """Prompt for search filters."""
    filters: SearchFilters = {}
    area = input_fn("Area (leave blank for any): ").strip()
    if area:
        filters["area"] = area
    max_budget = prompt_optional_float("Maximum monthly budget (leave blank for any): ", input_fn)
    if max_budget is not None:
        filters["max_budget"] = max_budget
    min_rating = prompt_optional_float("Minimum rating (leave blank for any): ", input_fn)
    if min_rating is not None:
        filters["min_rating"] = min_rating
    facilities = prompt_list("Required facilities (comma separated, blank for none): ", input_fn)
    if facilities:
        filters["required_facilities"] = facilities
    open_at = prompt_optional_int("Preferred time as HHMM (leave blank for any): ", input_fn)
    if open_at is not None:
        filters["open_at"] = open_at
    is_24_hours = prompt_yes_no("Only 24-hour gyms? (Y/N, blank to skip): ", input_fn)
    if is_24_hours is not None:
        filters["is_24_hours"] = is_24_hours
    classes = prompt_yes_no("Need classes? (Y/N, blank to skip): ", input_fn)
    if classes is not None:
        filters["classes_available"] = classes
    female_friendly = prompt_yes_no("Need a female-friendly gym? (Y/N, blank to skip): ", input_fn)
    if female_friendly is not None:
        filters["female_friendly"] = female_friendly
    gym_type = input_fn("Preferred gym type (leave blank for any): ").strip()
    if gym_type:
        filters["gym_type"] = gym_type
    user_x = prompt_optional_int(
        "Your X coordinate for distance sorting (blank to skip): ", input_fn
    )
    user_y = prompt_optional_int(
        "Your Y coordinate for distance sorting (blank to skip): ", input_fn
    )
    if user_x is not None and user_y is not None:
        filters["user_x"] = user_x
        filters["user_y"] = user_y
    return filters


def get_sort_key(input_fn: InputFn = input) -> str:
    """Prompt for a sorting choice."""
    options = {"1": "price", "2": "rating", "3": "distance", "4": "none"}
    print("\nSort results by:")
    print("1. Lowest price")
    print("2. Highest rating")
    print("3. Nearest distance")
    print("4. No sorting")
    while True:
        choice = input_fn("Choose an option: ").strip()
        if choice in options:
            return options[choice]
        print("Please enter 1-4.")


def run_search_flow(gyms: list[GymRecord], input_fn: InputFn = input) -> list[GymRecord]:
    """Run the interactive search workflow."""
    filters = get_search_filters(input_fn)
    matches = search_gyms(gyms, filters)
    sort_key = get_sort_key(input_fn)

    if sort_key == "distance":
        user_x = filters.get("user_x")
        user_y = filters.get("user_y")
        if user_x is None or user_y is None:
            print("Distance sorting skipped because coordinates were not provided.")
        else:
            matches = sort_gyms(matches, "distance", user_x=user_x, user_y=user_y)
    elif sort_key != "none":
        matches = sort_gyms(matches, sort_key)

    print("\nSearch results:\n")
    display_gyms(matches, filters.get("user_x"), filters.get("user_y"))
    return matches


def select_gyms_by_id(
    gyms: list[GymRecord],
    prompt: str,
    min_count: int,
    max_count: int,
    input_fn: InputFn = input,
) -> list[GymRecord]:
    """Prompt for gym IDs and return the matching records."""
    gym_lookup = {gym["gym_id"]: gym for gym in gyms}
    while True:
        raw_value = input_fn(prompt).strip()
        try:
            selected_ids = [int(item.strip()) for item in raw_value.split(",") if item.strip()]
        except ValueError:
            print("Please enter valid gym IDs separated by commas.")
            continue

        unique_ids = list(dict.fromkeys(selected_ids))
        if not min_count <= len(unique_ids) <= max_count:
            print(f"Please select between {min_count} and {max_count} gyms.")
            continue
        if any(gym_id not in gym_lookup for gym_id in unique_ids):
            print("One or more gym IDs were not found.")
            continue
        return [gym_lookup[gym_id] for gym_id in unique_ids]


def _build_comparison_rows(gyms: list[GymRecord]) -> list[list[str]]:
    """Build comparison table rows for display."""
    fields = [
        ("Gym Name", lambda gym: gym["gym_name"]),
        ("Area", lambda gym: gym["area"]),
        ("Monthly Price", lambda gym: f"${gym['monthly_price']:.2f}"),
        ("Day Pass", lambda gym: f"${gym['day_pass_price']:.2f}"),
        ("Rating", lambda gym: f"{gym['rating']:.1f}"),
        (
            "Hours",
            lambda gym: (
                "24 hours"
                if gym["is_24_hours"]
                else (
                    f"{format_time(gym['opening_time'], False)}-"
                    f"{format_time(gym['closing_time'], False)}"
                )
            ),
        ),
        ("Gym Type", lambda gym: gym["gym_type"]),
        ("Facilities", lambda gym: ", ".join(gym["facilities"])),
        ("Classes", lambda gym: "Yes" if gym["classes_available"] else "No"),
    ]
    rows: list[list[str]] = []
    for label, formatter in fields:
        rows.append([label, *[formatter(gym) for gym in gyms]])
    return rows


def compare_gyms(gyms: list[GymRecord], input_fn: InputFn = input) -> None:
    """Compare selected gyms in a table layout."""
    print("\nAvailable gyms:\n")
    display_gyms(gyms)
    selected = select_gyms_by_id(
        gyms,
        "Enter 2 or 3 gym IDs to compare (comma separated): ",
        min_count=2,
        max_count=3,
        input_fn=input_fn,
    )
    rows = _build_comparison_rows(selected)
    headers = ["Field", *[gym["gym_name"] for gym in selected]]
    widths = [max(len(row[index]) for row in [headers, *rows]) for index in range(len(headers))]

    print()
    print(" | ".join(cell.ljust(widths[index]) for index, cell in enumerate(headers)))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(" | ".join(cell.ljust(widths[index]) for index, cell in enumerate(row)))
    print()


def _collect_gym_details(
    gym_id: int,
    input_fn: InputFn = input,
    existing: GymRecord | None = None,
) -> GymRecord:
    """Prompt for gym details and build a record."""
    existing_record = cast(dict[str, Any], dict(existing)) if existing else None

    def current_value(key: str, fallback: str = "") -> str:
        if existing_record is None:
            return fallback
        value = existing_record.get(key, fallback)
        if isinstance(value, list):
            return ", ".join(value)
        return str(value)

    gym_name = (
        prompt_keep_or_non_empty(
            existing["gym_name"], f"Gym name [{current_value('gym_name')}]: ", input_fn
        )
        if existing
        else prompt_non_empty("Gym name: ", input_fn)
    )
    area = (
        prompt_keep_or_non_empty(existing["area"], f"Area [{current_value('area')}]: ", input_fn)
        if existing
        else prompt_non_empty("Area: ", input_fn)
    )
    address = (
        prompt_keep_or_non_empty(
            existing["address"], f"Address [{current_value('address')}]: ", input_fn
        )
        if existing
        else prompt_non_empty("Address: ", input_fn)
    )

    x_coordinate = prompt_optional_int(
        f"X coordinate [{current_value('x_coordinate', '0')}]: " if existing else "X coordinate: ",
        input_fn,
    )
    y_coordinate = prompt_optional_int(
        f"Y coordinate [{current_value('y_coordinate', '0')}]: " if existing else "Y coordinate: ",
        input_fn,
    )
    monthly_price = prompt_optional_float(
        f"Monthly price [{current_value('monthly_price', '0')}]: "
        if existing
        else "Monthly price: ",
        input_fn,
    )
    day_pass_price = prompt_optional_float(
        f"Day pass price [{current_value('day_pass_price', '0')}]: "
        if existing
        else "Day pass price: ",
        input_fn,
    )
    rating = prompt_optional_float(
        f"Rating [{current_value('rating', '0')}]: " if existing else "Rating: ",
        input_fn,
    )
    opening_time = prompt_optional_int(
        f"Opening time HHMM [{current_value('opening_time', '600')}]: "
        if existing
        else "Opening time HHMM: ",
        input_fn,
    )
    closing_time = prompt_optional_int(
        f"Closing time HHMM [{current_value('closing_time', '2200')}]: "
        if existing
        else "Closing time HHMM: ",
        input_fn,
    )
    is_24_hours = prompt_yes_no(
        f"24 hours? [{current_value('is_24_hours', 'False')}] (Y/N): "
        if existing
        else "24 hours? (Y/N): ",
        input_fn,
        allow_blank=existing is not None,
    )
    facilities_input = input_fn(
        f"Facilities [{current_value('facilities')}]: "
        if existing
        else "Facilities (comma separated): "
    ).strip()
    facilities = (
        [item.strip() for item in facilities_input.split(",") if item.strip()]
        if facilities_input
        else list(existing["facilities"])
        if existing
        else []
    )

    def bool_value(key: str, label: str) -> bool:
        default = bool(existing_record.get(key, False)) if existing_record else False
        answer = prompt_yes_no(
            f"{label} [{default}] (Y/N): " if existing else f"{label} (Y/N): ",
            input_fn,
            allow_blank=existing is not None,
        )
        return default if answer is None else answer

    return GymRecord(
        gym_id=gym_id,
        gym_name=gym_name,
        area=area,
        address=address,
        x_coordinate=existing["x_coordinate"]
        if x_coordinate is None and existing
        else x_coordinate or 0,
        y_coordinate=existing["y_coordinate"]
        if y_coordinate is None and existing
        else y_coordinate or 0,
        monthly_price=existing["monthly_price"]
        if monthly_price is None and existing
        else monthly_price or 0.0,
        day_pass_price=existing["day_pass_price"]
        if day_pass_price is None and existing
        else day_pass_price or 0.0,
        rating=existing["rating"] if rating is None and existing else rating or 0.0,
        opening_time=existing["opening_time"]
        if opening_time is None and existing
        else opening_time or 0,
        closing_time=existing["closing_time"]
        if closing_time is None and existing
        else closing_time or 2400,
        is_24_hours=existing["is_24_hours"]
        if is_24_hours is None and existing
        else bool(is_24_hours),
        gym_type=input_fn(
            f"Gym type [{current_value('gym_type')}]: " if existing else "Gym type: "
        ).strip()
        or (existing["gym_type"] if existing else "commercial"),
        facilities=facilities,
        beginner_friendly=bool_value("beginner_friendly", "Beginner-friendly"),
        female_friendly=bool_value("female_friendly", "Female-friendly"),
        student_discount=bool_value("student_discount", "Student discount"),
        peak_crowd_level=input_fn(
            f"Peak crowd level [{current_value('peak_crowd_level')}]: "
            if existing
            else "Peak crowd level (low/medium/high): "
        ).strip()
        or (existing["peak_crowd_level"] if existing else "medium"),
        parking_available=bool_value("parking_available", "Parking available"),
        near_mrt=bool_value("near_mrt", "Near MRT"),
        trainer_available=bool_value("trainer_available", "Trainer available"),
        classes_available=bool_value("classes_available", "Classes available"),
    )


def add_gym(gyms: list[GymRecord], input_fn: InputFn = input) -> None:
    """Collect and add a new gym record."""
    gym_id = generate_next_gym_id(gyms)
    new_gym = _collect_gym_details(gym_id, input_fn=input_fn)
    gyms.append(new_gym)
    save_database(gyms)
    print(f"\nGym '{new_gym['gym_name']}' added successfully.\n")


def update_gym_info(gyms: list[GymRecord], input_fn: InputFn = input) -> None:
    """Update an existing gym record."""
    print("\nExisting gyms:\n")
    display_gyms(gyms)
    gym_id = prompt_optional_int("Enter the gym ID to update: ", input_fn)
    if gym_id is None:
        print("No gym ID entered.")
        return
    for index, gym in enumerate(gyms):
        if gym["gym_id"] == gym_id:
            print("Press Enter to keep the current value shown in brackets.")
            updated_gym = _collect_gym_details(gym_id, input_fn=input_fn, existing=gym)
            gyms[index] = updated_gym
            save_database(gyms)
            print(f"\nGym '{updated_gym['gym_name']}' updated successfully.\n")
            return
    print("Gym ID not found.")


def manage_database(gyms: list[GymRecord], input_fn: InputFn = input) -> None:
    """Handle add/update flows for the dataset."""
    print("\nDatabase management:")
    print("1. Add a new gym")
    print("2. Update an existing gym")
    choice = input_fn("Choose an option: ").strip()
    if choice == "1":
        add_gym(gyms, input_fn)
    elif choice == "2":
        update_gym_info(gyms, input_fn)
    else:
        print("Invalid option.")


def main_menu(gyms: list[GymRecord], input_fn: InputFn = input) -> None:
    """Run the top-level menu loop."""
    while True:
        print("Gym and Fitness Centre Recommendation System")
        print("1. View all gyms")
        print("2. Search gyms by criteria")
        print("3. Compare shortlisted gyms")
        print("4. Add / update gym information")
        print("5. Exit")
        choice = input_fn("Select an option: ").strip()
        print()

        if choice == "1":
            display_all_gyms(gyms)
        elif choice == "2":
            run_search_flow(gyms, input_fn)
        elif choice == "3":
            compare_gyms(gyms, input_fn)
        elif choice == "4":
            manage_database(gyms, input_fn)
        elif choice == "5":
            print("Thank you for using the system.")
            return
        else:
            print("Invalid choice. Please enter 1-5.\n")
