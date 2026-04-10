# TUI Remove Buttons Design

## Summary
Remove the Search and Compare buttons from the Textual TUI. Searching and comparing will be triggered only by pressing Enter in the corresponding input fields. No other trigger mechanisms will be added.

## Goals
- Remove Search button from the Search screen UI.
- Remove Compare button from the Compare screen UI.
- Preserve Enter key behavior for both search and compare flows.

## Non-Goals
- No new key bindings or alternative triggers.
- No new UI hints unless explicitly requested.

## User Flow
- Search: User fills any search input and presses Enter to run search.
- Compare: User fills the IDs input and presses Enter to run compare.

## Implementation Notes
- Remove `Button("Search")` and `Button("Compare")` from the screen compositions.
- Keep `on_input_submitted` handlers as the only trigger.
- Remove `on_button_pressed` handlers if no longer needed.

## Testing
- Manual smoke test:
  - Search screen: Enter triggers search with a valid filter.
  - Compare screen: Enter triggers compare with valid IDs.

