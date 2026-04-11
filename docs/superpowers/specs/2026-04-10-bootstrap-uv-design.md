# Bootstrap UV Environment Design

## Goal

Make `bili2text bootstrap` responsible for turning a user's Provider / Feature choices into one correct `uv sync --extra ...` run, instead of leaving environment assembly to manual trial and error.

## Context

`uv sync --extra whisper` followed by `uv sync --extra web` does not create a combined environment. The second command replaces the first extra selection. In practice, users can easily end up with:

- only the last requested extra installed
- a half-broken `.venv` after repeated sync / uninstall attempts
- confusion about whether the project is a library or an application

The current refactor direction is "repository-as-application", so the bootstrap wizard is the right place to guide environment setup.

## Product Positioning

For this phase, `bili2text` is treated as an application project users clone and run with `uv`, not as a polished `pip install` library-first package.

That means bootstrap may assume:

- the user is inside the project repository
- `uv` is the standard environment manager
- the project should generate the exact sync command needed for the selected features

It should not silently install package managers or mutate global Python state.

## Requirements

### Functional

1. Bootstrap must detect whether `uv` is available on `PATH`.
2. If `uv` is missing, bootstrap must stop early and show install guidance.
3. Bootstrap must let the user choose:
   - interface language
   - enabled Providers
   - enabled Features
   - default Provider
   - provider-specific options
4. Bootstrap must derive a single combined list of extras from those choices.
5. Bootstrap must show the exact `uv sync --extra ...` command before execution.
6. Bootstrap must ask for confirmation before running the command.
7. Bootstrap must execute `uv sync` once with the combined extras.
8. Bootstrap must save config only after the environment step succeeds, or explicitly save partial config with a clear warning if we choose that path.
9. Bootstrap must provide a reusable "repair / resync" path so users can recover from broken environments without manually reconstructing the extras list.

### Non-Functional

1. Environment planning logic must be testable without interactive UI.
2. Bootstrap-specific copy must remain Chinese-first and go through i18n.
3. The implementation must keep the bootstrap flow understandable for non-developers.
4. We should avoid hidden side effects such as auto-installing `uv`.

## Architecture

Split the work into two layers:

### 1. Pure environment planning layer

Add small testable helpers that:

- validate `uv` availability
- normalize selected Providers / Features
- map those selections to extras
- build the final `uv sync` command
- expose human-readable status / error messages

This layer should not depend on InquirerPy.

### 2. Interactive bootstrap layer

Keep Bootstrap as the orchestrator:

- collect selections from the user
- render summaries with Rich
- call the environment planning helpers
- confirm and run `uv sync`
- save config when the sync succeeds

## Data Model Changes

`AppConfig` should persist both:

- `enabled_providers`
- `enabled_features`

This allows bootstrap to regenerate the environment later and enables a dedicated repair/resync command.

## Provider / Feature to Extra Mapping

### Providers

- `whisper` -> `whisper`
- `sensevoice` -> `sensevoice`
- `volcengine` -> `volcengine`

### Features

- `web` -> `web`
- `server` -> `server`
- `window` -> no extra for now

We should deduplicate extras and keep output order stable for predictable docs and tests.

## UV Strategy

### If `uv` exists

- show the exact command
- ask for confirmation
- run it in the repo root

### If `uv` is missing

- print platform-appropriate install guidance
- do not attempt to install `uv` automatically
- stop bootstrap with a clear non-zero outcome

### If `uv sync` fails

- surface the command and stderr/stdout summary
- tell the user how to retry
- do not pretend the environment is ready

## Resync / Repair Path

Add a reusable command path, likely `bili2text bootstrap --sync-only` or a dedicated CLI command such as `bili2text env sync`, that:

- loads the saved config
- rebuilds the extras list
- reruns the exact `uv sync --extra ...` command

This should be the official fix path for broken environments.

## Testing Strategy

1. Unit-test extras derivation from provider / feature selections.
2. Unit-test command construction.
3. Unit-test missing-`uv` detection.
4. Unit-test config round-trip for `enabled_features`.
5. Unit-test bootstrap resync logic via injectable command runners.
6. Keep the existing CLI / config tests green.

## Risks

### Dirty `.venv`

Repeated sync attempts can leave a damaged environment. We should not try to solve every wheel uninstall edge case inside bootstrap, but we should give users a clear recovery path.

### Scope creep

Bootstrap should manage project environment selection, not become a general Python installer.

## Out of Scope

- auto-installing `uv`
- publishing a standalone binary installer
- fully solving every corrupted virtualenv state
- redesigning the web frontend visuals
