# Contributing to Claude YOLO Mode

Thank you for considering contributing! This project balances maximum Claude Code autonomy with maximum safety.

## Design Principles

1. **Safety First**: Every feature should consider security implications
2. **User Protection**: Target users may be inexperienced - protect them from common mistakes
3. **Transparency**: All actions should be logged appropriately
4. **Balance**: Maximum capability within safety constraints
5. **Documentation**: Keep docs updated with changes

## Target Users

Remember that this environment is designed for:
- Sales engineers doing demos
- Forward-deployed engineers in customer environments
- CTOs and leadership experimenting
- Anyone who may be disconnected from architecture details

These users need protection from themselves AND from potential misconfigurations.

## Areas for Contribution

### Safety Enhancements
- Additional secrets detection patterns
- More git safety hooks
- Resource limit improvements
- Additional dangerous command detection

### Tooling
- Additional cloud provider CLIs
- More database clients
- Language-specific toolchains (Go, Rust, Node.js)
- Additional MCP servers

### Documentation
- Usage examples
- Troubleshooting guides
- Corporate deployment patterns
- Integration guides

### Testing
- Container build tests
- Safety feature validation
- Performance benchmarks

## Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-safety`)
3. Make your changes
4. Test thoroughly:
   ```bash
   make build
   make test
   make shell
   # Test your feature
   ```
5. Update documentation (README.md, CLAUDE.md)
6. Submit a pull request

## Testing Checklist

Before submitting a PR:

- [ ] Container builds successfully
- [ ] Safety features work as expected
- [ ] Logs are generated appropriately
- [ ] No secrets or credentials in commits
- [ ] Documentation updated
- [ ] Changes don't break existing workflows
- [ ] Tested with actual Claude Code usage

## Code Style

- **Shell scripts**: Follow shellcheck recommendations
- **Python**: Use ruff for formatting and linting
- **Dockerfile**: Follow best practices (multi-stage builds, layer caching)
- **Documentation**: Clear, concise, with examples

## Safety Considerations

When adding features:

1. **Secrets**: Will this feature handle sensitive data?
2. **Destructive**: Could this cause data loss?
3. **Network**: Does this make external requests?
4. **Resources**: Could this consume excessive CPU/memory/disk?
5. **Permissions**: Does this need elevated privileges?

If yes to any, ensure appropriate:
- Logging
- Validation
- User warnings
- Safety checks

## Questions?

Open an issue for:
- Feature requests
- Bug reports
- Documentation improvements
- Questions about design decisions

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
