# ui/graph_component.py
#
# Declares the custom React + Cytoscape.js component that replaces
# streamlit_cytoscapejs. Both editors (problem graph, rulebook) reuse the
# same compiled frontend bundle and are told apart by the "mode" prop.
#
# NOTE: Streamlit custom components keep returning the *last* value the
# frontend sent on every rerun -- they don't reset to None on their own.
# Without _dedupe below, a single click would get dispatched over and
# over on every later rerun (including ones triggered by unrelated
# sidebar edits), against state that's already changed -- that's what
# caused the "Unknown rule 'r1'" / "Invalid equivalence class selection"
# crashes. index.jsx stamps a unique _seq onto every event; we just
# remember the last _seq we've already handled per component key.

import os
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


_FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
_FRONTEND_BUILD_DIR = _FRONTEND_DIR / "build"

# Production uses the compiled frontend committed to the repository.
# Local development can opt into the Vite server by defining
# GRAPH_EDITOR_DEV_URL=http://localhost:5173.
_DEV_URL = os.environ.get("GRAPH_EDITOR_DEV_URL")

if _DEV_URL:
    _component = components.declare_component(
        "graph_editor",
        url=_DEV_URL,
    )
else:
    if not (_FRONTEND_BUILD_DIR / "index.html").exists():
        raise RuntimeError(
            "The graph editor frontend has not been built. "
            "Run `npm ci` and `npm run build` inside viz/frontend."
        )

    _component = components.declare_component(
        "graph_editor",
        path=str(_FRONTEND_BUILD_DIR),
    )


# Ignore an event we've already dispatched once.
def _dedupe(raw_event, dedupe_key):
    if raw_event is None:
        return None

    seen_key = f"_graph_component_last_seq::{dedupe_key}"
    seq = raw_event.get("_seq")

    if seq is not None and seq == st.session_state.get(seen_key):
        return None

    st.session_state[seen_key] = seq
    return raw_event


# Render the interactive problem graph editor.
# Returns one event dict (see viz/ui/problem_graph_dispatch.py) or None
# if nothing happened since the last rerun.
def problem_graph_editor(elements, stylesheet, rule_names, key=None):
    raw_event = _component(
        mode="problem_graph",
        elements=elements,
        stylesheet=stylesheet,
        rule_names=rule_names,
        key=key,
        default=None,
    )
    return _dedupe(raw_event, key or "problem_graph")


# Render the interactive rulebook editor.
# Returns one event dict (see viz/ui/rulebook_dispatch.py) or None
# if nothing happened since the last rerun.
def rulebook_editor(elements, stylesheet, key=None):
    raw_event = _component(
        mode="rulebook",
        elements=elements,
        stylesheet=stylesheet,
        key=key,
        default=None,
    )
    return _dedupe(raw_event, key or "rulebook")
