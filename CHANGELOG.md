# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.1] - 2026-01-18

### Changed

- Rename release artifacts from `slack-*` to `slackasme-*` for consistency
- Command name changed from `slack` to `slackasme`
- Custom homebrew update script for multi-platform formula

## [0.2.0] - 2026-01-18

### Changed

- **BREAKING**: Rename project from `slack-cli` to `slackasme` to avoid namespace conflict with Slack's official CLI
- **BREAKING**: Config path changed from `~/.config/slack-cli/` to `~/.config/slackasme/`
- Homebrew formula renamed: `brew install slackasme`
- GitHub repo renamed: `joh90/slackasme`

## [0.1.0] - 2026-01-18

### Added

- Initial release
- **Auth commands**: `auth test`, `auth configure`, `auth logout`
- **Message commands**: `message send`, `message list`, `message thread`, `message schedule`, `message delete`
- **Channel commands**: `channel list`, `channel info`
- **User commands**: `user list`, `user info`
- **DM commands**: `dm open` (single user and group DM)
- **Reaction commands**: `reaction add`, `reaction remove`
- **File commands**: `file upload`, `file list`
- **Search commands**: `search messages`, `search users`
- Smart user resolution (ID, email, or username)
- JSON output (`--json` flag) for scripting
- Verbose/debug logging (`--verbose`, `--debug`)
- Secure token storage (`~/.config/slackasme/token` with 600 permissions)
- Token masking in error output
- Rate limit handling via SDK retry handler
- Input validation for all commands
- 92 tests with 83% coverage

### Security

- Email validation regex: `^[^@\s]+@[^@\s]+\.[^@\s]+$`
- User ID pattern validation: `^U[A-Z0-9]{8,12}$`
- File path validation (exists, size limit, no traversal)
- Token masking in all error output

[Unreleased]: https://github.com/joh90/slackasme/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/joh90/slackasme/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/joh90/slackasme/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/joh90/slackasme/releases/tag/v0.1.0
