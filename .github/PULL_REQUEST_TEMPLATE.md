## Description

Provide a summary of the changes, including the motivation and the issue fixed
(if applicable).

- **Motivation**: Why is this change necessary?
- **Fixes Issue**: # (link the issue)

---

## Change Type

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to
      not work as expected)
- [ ] Documentation / housekeeping

---

## Testing Instructions

- [ ] `python3 -m pytest tests/`
- [ ] `flake8 src/ tests/` when Python sources changed
- [ ] `mypy src/` when Python sources changed
- [ ] `MPLBACKEND=Agg` set if running the processor/validator

---

## Checklist

- [ ] Code adheres to project style guidelines.
- [ ] A self-review has been performed.
- [ ] Documentation has been updated as necessary.
- [ ] No secrets, credentials, or local env files included.
- [ ] Unit tests pass locally.
