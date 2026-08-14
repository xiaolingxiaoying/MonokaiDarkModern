# Monokai Dark Modern

Sublime Text 4 theme package with a calm warm-black UI and the original
Monokai code palette. The UI uses `#171815`; editor buffers use `#242422`.

## Install

Copy this folder into `%APPDATA%\Sublime Text\Packages\Monokai Dark Modern`.
Then use **Preferences → Package Settings → Monokai Dark Modern** to select
the UI theme and color scheme. Selecting the UI theme enables the bundled
rounded, equal-width 180px file tabs.

The generated `Monokai Dark Modern.sublime-color-scheme` is checked in. To
rebuild it after mapping changes, run `python tools/build_theme.py`; use
`--check` to validate without writing files.

LSP semantic highlighting is optional. Install Sublime's LSP package and set
`"semantic_highlighting": true` in `LSP.sublime-settings` when desired.

The bundled Monokai source is attributed in [LICENSE](LICENSE).
