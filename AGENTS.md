# macOS native game runtime packaging

- Keep the WIE runtime pinned; apply focused patches rather than duplicating engine code.
- Native Cocoa/winit window only. No WebView, browser or localhost server.
- Do not commit APKs, game data, saves, binaries, credentials, or absolute local paths.
- Runtime changes belong in patches/; packaging belongs in package.py.
- Run cargo fmt and cargo clippy --workspace before committing runtime changes; run relevant behavioral tests.
- Verify the actual app launch, keyboard input, save/reload and architecture before claiming completion.
