from gym_recommender.tui import resolve_area_match


def test_resolve_area_single_match_substring() -> None:
    areas = ["Jurong East", "Bedok"]
    match, message = resolve_area_match("Jurong", areas)
    assert match == "Jurong East"
    assert message == "Using area 'Jurong East' for 'Jurong'."


def test_resolve_area_case_insensitive() -> None:
    areas = ["Jurong East", "Bedok"]
    match, message = resolve_area_match("juRoNg", areas)
    assert match == "Jurong East"
    assert message == "Using area 'Jurong East' for 'juRoNg'."


def test_resolve_area_multiple_matches() -> None:
    areas = ["Jurong East", "Paya Lebar", "Bedok"]
    match, message = resolve_area_match("a", areas)
    assert match is None
    assert message == "Area 'a' matches multiple areas: Jurong East, Paya Lebar."


def test_resolve_area_no_match() -> None:
    areas = ["Jurong East", "Bedok"]
    match, message = resolve_area_match("Unknown", areas)
    assert match is None
    assert message == "Area 'Unknown' not found. Try: Jurong East, Bedok."
