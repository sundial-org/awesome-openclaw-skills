# Rails + Docker builds on Fly (common failure patterns)

## Symptom: Bundler can't find platform gem (e.g., nokogiri)

Example:
- `Could not find nokogiri-...-x86_64-linux in locally installed gems`

Cause:
- `Gemfile.lock` was generated on macOS only (darwin platforms), but Fly builds on Linux.

Fix:
- Add the target platform(s) to the lockfile and commit:
  - `bundle lock --add-platform x86_64-linux`
  - (optional) `bundle lock --add-platform aarch64-linux`

## Symptom: build uses wrong Ruby version

Clue:
- stacktrace paths like `/ruby/3.1.0/...` when app expects Ruby 3.2.x

Fix:
- Ensure Dockerfile `ARG RUBY_VERSION=...` matches `.ruby-version`.

## Symptom: bootsnap precompile fails in Docker build

Clue:
- failure during `bundle exec bootsnap precompile ...`

Fix checklist:
- confirm gems are installed for the platform
- confirm lockfile platforms include Linux
- run `bundle install` in the builder stage after any lockfile surgery

## Tip: prefer remote builder when local env differs

- `fly deploy --remote-only`
