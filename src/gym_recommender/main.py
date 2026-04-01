"""Console entrypoint for the gym recommendation system."""

from __future__ import annotations

from gym_recommender.data import load_database
from gym_recommender.ui import main_menu


def main() -> None:
    """Load data and start the interactive menu."""
    gyms = load_database()
    main_menu(gyms)


if __name__ == "__main__":
    main()
