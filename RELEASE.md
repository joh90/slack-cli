# Release Process

## Overview

Releases are automated via GitHub Actions. Pushing a version tag triggers the full release pipeline.

```
git tag v0.1.0 → git push origin v0.1.0 → GitHub Actions
                                               │
                                               ▼
                                         ┌───────────┐
                                         │   test    │
                                         │(lint+test)│
                                         └─────┬─────┘
                                               │
                                               ▼
                                         ┌───────────┐
                                         │   build   │
                                         │(3 runners)│
                                         └─────┬─────┘
                                               │
                 ┌─────────────────────────────┼─────────────────────────────┐
                 ▼                             ▼                             ▼
          macos-latest                 macos-15-intel                ubuntu-latest
          (ARM64 M1+)                    (Intel x86)                 (Linux x86)
                 │                             │                             │
                 └─────────────────────────────┼─────────────────────────────┘
                                               │
                                               ▼
                                         ┌───────────┐
                                         │  release  │
                                         │(GH Release│
                                         └─────┬─────┘
                                               │
                                               ▼
                                         ┌───────────┐
                                         │ homebrew  │
                                         │(update tap│
                                         └───────────┘
```

## Jobs

| Job | Purpose |
|-----|---------|
| **test** | Runs linter (`ruff`) + tests (`pytest`) to validate code |
| **build** | PyInstaller builds binary on each OS, generates SHA256 checksum |
| **release** | Downloads artifacts, creates GitHub Release with binaries and checksums |
| **homebrew** | Updates `joh90/homebrew-tap` formula with new version and SHA256 |

## Release Commands

### 1. Update Version

Update the version in `slackasme/__init__.py`:

```python
__version__ = "0.2.0"
```

Commit and push:

```bash
git add -A && git commit -m "Bump version to 0.2.0" && git push origin main
```

### 2. Create and Push Tag

```bash
# Create tag
git tag v0.2.0

# Push tag to trigger release
git push origin v0.2.0
```

### 3. Monitor Workflow

```bash
# Watch the release workflow
gh run watch

# Or view in browser
gh run view --web
```

### 4. Verify Release

```bash
# Check release was created
gh release view v0.1.0

# List release assets
gh release view v0.1.0 --json assets --jq '.assets[].name'
```

### 5. Test Homebrew Installation

```bash
# Add tap (first time only)
brew tap joh90/tap

# Install or upgrade
brew install slackasme
# or
brew upgrade slackasme

# Verify
slackasme --version
```

## Artifacts

Each release includes:

| File | Platform |
|------|----------|
| `slack-darwin-arm64` | macOS Apple Silicon (M1/M2/M3) |
| `slack-darwin-amd64` | macOS Intel |
| `slack-linux-amd64` | Linux x86_64 |
| `*.sha256` | SHA256 checksums for each binary |

## Versioning

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** (`v1.0.0` → `v2.0.0`): Breaking changes
- **MINOR** (`v1.0.0` → `v1.1.0`): New features, backwards compatible
- **PATCH** (`v1.0.0` → `v1.0.1`): Bug fixes, backwards compatible

## Troubleshooting

### Workflow Failed

```bash
# View failed run logs
gh run view --log-failed

# Re-run failed jobs
gh run rerun <run-id> --failed
```


