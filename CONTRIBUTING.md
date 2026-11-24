# Contributing

Thank you for your interest in STISim.

## Development Workflow

1. Open an issue describing the bug, feature, or scientific-modeling question.
2. Create a branch for the change.
3. Add or update tests when the change affects model behavior.
4. Run `pytest` before opening a pull request.
5. Describe any scientific assumptions, parameter changes, or reproducibility impacts in the pull request.

## Model Changes

Changes to transmission, vaccination, screening, treatment, PID, relationship formation, or demographic processes should include:

- a clear explanation of the mechanism being changed,
- references or rationale for new parameter values,
- a note about whether published simulation outputs are expected to change.

## Code Style

Keep changes focused and readable. Prefer small functions with explicit inputs over hidden global state. Avoid changing calibrated parameters unless the change is intentional and documented.

## Support

Issues are the preferred place for support requests, bug reports, and reproducibility questions.
