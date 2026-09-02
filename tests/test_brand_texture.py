"""Verge-style band texture + brand naming regression tests.

Static (AST/string) checks - no tkinter/display needed, CI-safe:

* theme_manager ships draw_band_texture (abstract circles, header+footer
  variants) and stores settings under GFH-Telecom (prefix in caps).
* Both app files paint the texture on their inline header band and
  copyright bar, and instantiate ThemeManager with app_name="VidaPay-GFH".
* header_manager paints header + footer bands for apps that use it and
  keeps the lazy-tkinter import that prevents a frozen-exe NameError.
"""
import ast
import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]

THEME_MANAGER = ROOT / "theme_manager.py"
HEADER_MANAGER = ROOT / "header_manager.py"

APP_FILES = [
    ROOT / "GFH_Inventory_Audit.py",
    ROOT / "GFH_Inventory_Audit_Timesheet.py",
]


def _source(path):
    assert path.exists(), f"missing expected source file: {path}"
    return path.read_text(encoding="utf-8")


def _parse(path):
    return ast.parse(_source(path))


# ── theme_manager: texture painter + GFH-Telecom prefix ──

def test_theme_manager_has_band_texture_painter():
    tree = _parse(THEME_MANAGER)
    names = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert "draw_band_texture" in names


def test_band_texture_draws_ovals_for_header_and_footer():
    src = _source(THEME_MANAGER)
    assert "create_oval" in src
    # Both variants exist and are brand-fixed colors.
    assert "_HEADER_CIRCLES" in src
    assert "_FOOTER_CIRCLES" in src
    assert '"header"' in src and '"footer"' in src
    # Resize-safe: geometry recomputed from the canvas each call.
    assert "winfo_width" in src and "winfo_height" in src


def test_band_texture_items_stay_below_text():
    src = _source(THEME_MANAGER)
    assert 'tag_lower("band_texture")' in src


def test_config_dir_uses_caps_prefix():
    src = _source(THEME_MANAGER)
    assert '"GFH-Telecom"' in src
    assert '"gfh-telecom"' not in src


# ── header_manager: texture on both bands + frozen-exe import fix ──

def test_header_manager_paints_header_and_footer_bands():
    src = _source(HEADER_MANAGER)
    assert "draw_band_texture" in src
    assert 'painter(canvas, "header")' in src
    assert 'painter(canvas, "footer")' in src
    assert "band_title" in src and "band_text" in src


def test_header_manager_canvas_stacks_above_title_label():
    src = _source(HEADER_MANAGER)
    assert "self.texture_canvas.lift(self.title_label)" in src
    assert "self.footer_canvas.lift(self.copyright_label)" in src


def test_header_manager_keeps_lazy_tkinter_import_in_add_copyright():
    src = _source(HEADER_MANAGER)
    # Regression guard: frozen exe crashed with NameError: tk without it.
    assert re.search(
        r"def add_copyright\(.*?\)\s*:\s*\n(?:.*\n)*?\s*import tkinter as tk",
        _source(HEADER_MANAGER),
    ), "add_copyright must import tkinter lazily before using tk"


# ── apps: texture wired into inline bands + VidaPay-GFH naming ──

@pytest.mark.parametrize("app_path", APP_FILES, ids=lambda p: p.name)
def test_app_paints_band_texture(app_path):
    src = _source(app_path)
    assert "from theme_manager import draw_band_texture" in src
    assert "_repaint_band" in src
    assert "_repaint_footer_bar" in src
    assert "band_canvas.lift(_title_lbl)" in src
    assert "footer_canvas.lift(_clbl)" in src


@pytest.mark.parametrize("app_path", APP_FILES, ids=lambda p: p.name)
def test_app_uses_vidapay_gfh_app_name(app_path):
    src = _source(app_path)
    assert 'app_name="VidaPay-GFH"' in src
    assert "vidapay-gfh" not in src


def test_no_lowercase_gfh_prefix_in_settings_paths():
    for app_path in APP_FILES:
        src = _source(app_path)
        assert '"gfh-telecom"' not in src
