"""
style_loader.py
───────────────
Utility for injecting external CSS into a Streamlit app.

Usage in main.py:
    from style_loader import load_css
    load_css("styles.css")
"""

import streamlit as st
from pathlib import Path


def load_css(css_file: str) -> None:
    """Read a CSS file and inject it into the Streamlit app via st.markdown."""
    css_path = Path(css_file)
    if not css_path.exists():
        st.warning(f"Stylesheet not found: {css_file}")
        return
    css = css_path.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)