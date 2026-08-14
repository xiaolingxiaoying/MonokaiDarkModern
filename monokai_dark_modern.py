"""Commands for Monokai Dark Modern; normal highlighting stays static."""

from __future__ import annotations

import importlib
import json

import sublime
import sublime_plugin


SCHEME = "Monokai Dark Modern.sublime-color-scheme"
UI_THEME = "Monokai Dark Modern.sublime-theme"


def _semantic_token(view: sublime.View, point: int):
    try:
        registry = importlib.import_module("LSP.plugin.core.registry")
        listener = registry.windows.listener_for_view(view)
        if listener:
            for session_view in listener.session_views_async():
                for token in session_view.session_buffer.get_semantic_tokens():
                    if token.region.contains(point) and point < token.region.end():
                        return token, session_view.session.config.name
    except Exception:
        return None
    return None


class MonokaiDarkModernSelectColorSchemeCommand(sublime_plugin.ApplicationCommand):
    def run(self) -> None:
        resources = sublime.find_resources(SCHEME)
        settings = sublime.load_settings("Preferences.sublime-settings")
        settings.set("color_scheme", resources[0] if resources else "Packages/Monokai Dark Modern/" + SCHEME)
        sublime.save_settings("Preferences.sublime-settings")
        sublime.status_message("Monokai Dark Modern color scheme selected")


class MonokaiDarkModernSelectUiThemeCommand(sublime_plugin.ApplicationCommand):
    def run(self) -> None:
        settings = sublime.load_settings("Preferences.sublime-settings")
        settings.set("theme", UI_THEME)
        sublime.save_settings("Preferences.sublime-settings")
        sublime.status_message("Monokai Dark Modern UI theme selected")


class MonokaiDarkModernInspectHighlightCommand(sublime_plugin.WindowCommand):
    def run(self) -> None:
        view = self.window.active_view()
        if not view:
            sublime.status_message("No active view to inspect")
            return
        point = view.sel()[0].begin() if view.sel() else 0
        scope = view.scope_name(point).strip()
        style = view.style_for_scope(scope)
        semantic = _semantic_token(view, point)
        message = ["Monokai Dark Modern — Highlight Inspector", "", f"Scopes: {scope or '(none)'}", f"Foreground: {style.get('foreground', '(default)')}"]
        if semantic:
            token, server = semantic
            message.append(f"Semantic token: {token.type} [{', '.join(token.modifiers) or 'no modifiers'}] via {server}")
        else:
            message.append("Semantic token: (none)")
        sublime.message_dialog("\n".join(message))


class MonokaiDarkModernCheckSemanticHighlightingCommand(sublime_plugin.WindowCommand):
    def run(self) -> None:
        settings_resources = sublime.find_resources("LSP.sublime-settings")
        enabled = bool(settings_resources and sublime.load_settings("LSP.sublime-settings").get("semantic_highlighting", False))
        if not settings_resources:
            message = "Sublime LSP was not detected. Base syntax highlighting is active."
        elif enabled:
            message = "LSP semantic highlighting is enabled. Server support determines per-language availability."
        else:
            message = 'LSP is installed but semantic highlighting is disabled. Set "semantic_highlighting": true in LSP.sublime-settings to enable it.'
        sublime.message_dialog(message)

