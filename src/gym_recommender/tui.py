from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    Checkbox,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Static,
)

from gym_recommender.data import load_database
from gym_recommender.models import GymRecord, SearchFilters
from gym_recommender.search import search_gyms
from gym_recommender.services import compare_gym_records


@dataclass
class GymListItem:
    gym: GymRecord

    def render_label(self) -> str:
        return f"[{self.gym['gym_id']}] {self.gym['gym_name']} • {self.gym['area']}"


def _format_gym_details(gym: GymRecord) -> str:
    facilities = ", ".join(gym["facilities"])
    hours = (
        "24 hours"
        if gym["is_24_hours"]
        else f"{gym['opening_time']:04d}-{gym['closing_time']:04d}"
    )
    return (
        f"{gym['gym_name']} ({gym['area']})\n"
        f"Address: {gym['address']}\n"
        f"Price: ${gym['monthly_price']:.2f}/month | Day pass ${gym['day_pass_price']:.2f}\n"
        f"Rating: {gym['rating']:.1f} | Type: {gym['gym_type']} | Hours: {hours}\n"
        f"Facilities: {facilities}"
    )


def _parse_optional_int(value: str) -> int | None:
    cleaned = value.strip()
    return int(cleaned) if cleaned.isdigit() else None


def _parse_optional_float(value: str) -> float | None:
    cleaned = value.strip()
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


class BrowseScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        with Container():
            yield Label("Browse gyms", id="browse-title")
            with Horizontal():
                yield ListView(id="browse-list")
                yield Static("Select a gym to view details.", id="browse-details")

    def on_mount(self) -> None:
        list_view = self.query_one("#browse-list", ListView)
        for gym in self.app.get_gyms():
            item = GymListItem(gym)
            list_item = ListItem(Label(item.render_label()))
            list_item.data = item
            list_view.append(list_item)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        details = self.query_one("#browse-details", Static)
        item = getattr(event.item, "data", None)
        if isinstance(item, GymListItem):
            details.update(_format_gym_details(item.gym))


class SearchScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        with Vertical():
            yield Label("Search gyms", id="search-title")
            with Container(classes="search-form"):
                yield Input(placeholder="Area", id="search-area")
                yield Input(placeholder="Max budget", id="search-max-budget")
                yield Input(placeholder="Min rating", id="search-min-rating")
                yield Input(placeholder="Facilities (comma separated)", id="search-facilities")
                yield Input(placeholder="Open at (HHMM)", id="search-open-at")
                yield Input(placeholder="Gym type", id="search-gym-type")
                yield Input(placeholder="User X coordinate", id="search-user-x")
                yield Input(placeholder="User Y coordinate", id="search-user-y")
                yield Checkbox("24-hour only", id="search-24-hours")
                yield Checkbox("Classes available", id="search-classes")
                yield Checkbox("Female-friendly", id="search-female")
                yield Button("Search", id="search-submit", variant="primary")
                yield Static("Enter filters and press Search.", id="search-status")
            yield ListView(id="search-results")

    def _collect_filters(self) -> SearchFilters:
        filters: SearchFilters = {}
        area = self.query_one("#search-area", Input).value.strip()
        if area:
            filters["area"] = area
        max_budget = _parse_optional_float(self.query_one("#search-max-budget", Input).value)
        if max_budget is not None:
            filters["max_budget"] = max_budget
        min_rating = _parse_optional_float(self.query_one("#search-min-rating", Input).value)
        if min_rating is not None:
            filters["min_rating"] = min_rating
        facilities_raw = self.query_one("#search-facilities", Input).value.strip()
        if facilities_raw:
            filters["required_facilities"] = [
                item.strip() for item in facilities_raw.split(",") if item.strip()
            ]
        open_at = _parse_optional_int(self.query_one("#search-open-at", Input).value)
        if open_at is not None:
            filters["open_at"] = open_at
        gym_type = self.query_one("#search-gym-type", Input).value.strip()
        if gym_type:
            filters["gym_type"] = gym_type
        user_x = _parse_optional_int(self.query_one("#search-user-x", Input).value)
        user_y = _parse_optional_int(self.query_one("#search-user-y", Input).value)
        if user_x is not None and user_y is not None:
            filters["user_x"] = user_x
            filters["user_y"] = user_y
        if self.query_one("#search-24-hours", Checkbox).value:
            filters["is_24_hours"] = True
        if self.query_one("#search-classes", Checkbox).value:
            filters["classes_available"] = True
        if self.query_one("#search-female", Checkbox).value:
            filters["female_friendly"] = True
        return filters

    def _run_search(self) -> None:
        status = self.query_one("#search-status", Static)
        results_view = self.query_one("#search-results", ListView)
        filters = self._collect_filters()
        gyms = search_gyms(self.app.get_gyms(), filters)
        results_view.clear()
        for gym in gyms:
            item = GymListItem(gym)
            list_item = ListItem(Label(item.render_label()))
            list_item.data = item
            results_view.append(list_item)
        status.update(f"Found {len(gyms)} gyms.")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "search-submit":
            self._run_search()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id and event.input.id.startswith("search-"):
            self._run_search()


class CompareScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        with Vertical():
            yield Label("Compare gyms", id="compare-title")
            with Horizontal():
                yield Input(placeholder="Gym IDs (e.g. 1,2)", id="compare-ids")
                yield Button("Compare", id="compare-submit", variant="primary")
            yield Static("Enter 2 or 3 IDs to compare.", id="compare-status")
            yield DataTable(id="compare-table")

    def _build_table(self, gyms: Iterable[dict[str, Any]]) -> None:
        table = self.query_one("#compare-table", DataTable)
        table.clear(columns=True)
        gyms_list = list(gyms)
        if not gyms_list:
            return
        table.add_column("Field")
        for gym in gyms_list:
            table.add_column(str(gym.get("gym_name", "Gym")))
        fields = [
            ("Area", "area"),
            ("Monthly Price", "monthly_price"),
            ("Day Pass", "day_pass_price"),
            ("Rating", "rating"),
            ("Gym Type", "gym_type"),
            ("Facilities", "facilities"),
        ]
        for label, key in fields:
            row = [label]
            for gym in gyms_list:
                value = gym.get(key, "")
                if isinstance(value, list):
                    value = ", ".join(value)
                if isinstance(value, float):
                    value = f"{value:.2f}"
                row.append(str(value))
            table.add_row(*row)

    def _run_compare(self) -> None:
        status = self.query_one("#compare-status", Static)
        ids_raw = self.query_one("#compare-ids", Input).value
        parsed = [int(item) for item in ids_raw.split(",") if item.strip().isdigit()]
        unique_ids = list(dict.fromkeys(parsed))
        if len(unique_ids) < 2 or len(unique_ids) > 3:
            status.update("Please enter 2 or 3 unique IDs.")
            self.query_one("#compare-table", DataTable).clear(columns=True)
            return
        try:
            gyms = compare_gym_records(unique_ids)
        except ValueError as exc:
            status.update(str(exc))
            self.query_one("#compare-table", DataTable).clear(columns=True)
            return
        self._build_table(gyms)
        status.update("Comparison ready.")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "compare-submit":
            self._run_compare()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "compare-ids":
            self._run_compare()


class GymTuiApp(App):
    CSS = """
    Screen {
      padding: 1;
    }

    #browse-title, #search-title, #compare-title {
      padding: 0 0 1 0;
      text-style: bold;
    }

    #browse-list, #search-results {
      width: 1fr;
      height: 1fr;
    }

    #browse-details {
      width: 2fr;
      height: 1fr;
      border: solid $primary;
      padding: 1;
    }

    .search-form {
      padding: 1 0;
      border-bottom: solid $panel;
    }

    #compare-table {
      height: 1fr;
    }
    """

    BINDINGS = [
        ("b", "show_browse", "Browse"),
        ("s", "show_search", "Search"),
        ("c", "show_compare", "Compare"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._gyms = load_database()

    def get_gyms(self) -> list[GymRecord]:
        return list(self._gyms)

    def on_mount(self) -> None:
        self.install_screen(BrowseScreen(), name="browse")
        self.install_screen(SearchScreen(), name="search")
        self.install_screen(CompareScreen(), name="compare")
        self.push_screen("browse")

    def action_show_browse(self) -> None:
        self.switch_screen("browse")

    def action_show_search(self) -> None:
        self.switch_screen("search")

    def action_show_compare(self) -> None:
        self.switch_screen("compare")


def build_app() -> GymTuiApp:
    return GymTuiApp()


def main() -> None:
    build_app().run()
