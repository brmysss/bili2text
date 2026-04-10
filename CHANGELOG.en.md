# Changelog

## 2026-04-10

### Refactor Foundation

- established `src/b2t` as the new core directory
- introduced a CLI-first architecture with `transcribe / web / server / window`
- reduced downloads to a single `yt-dlp` path
- added bootstrap onboarding and local config support

### Providers

- added local `whisper`
- added local `sensevoice`
- added Volcengine provider scaffolding and config support

### UX and I18n

- made CLI help Chinese-first
- added short aliases: `tx / init / ui / srv / win / diag / lang`
- added the `language` / `lang` command
- upgraded bootstrap into an interactive wizard with provider explanations
- wired i18n into the web UI and Tk window feature

### Docs and Cleanup

- rewrote the README as a bilingual project front door
- added development docs
- moved legacy scripts and old dependency files into `archive/`
- moved logos and favicon into `assets/`
