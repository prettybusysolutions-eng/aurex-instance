# ClawHub Packaging Requirements

Last updated: 2026-04-13 21:12 EDT
Status: READY

## Required surfaces
- `SKILL.md`
- clear description
- installable folder structure
- versioned publish command via `clawhub publish`

## Publish pattern
```bash
clawhub publish ./path-to-skill --slug runtime-doctor --name "Runtime Doctor" --version 0.1.0 --changelog "Initial release"
```

## For stronger verification
- clear README
- safe non-destructive behavior
- explicit usage instructions
- public repo with documentation
- stable package structure

## Runtime Doctor fit
Good candidate for ClawHub as a troubleshooting/installable utility skill.
