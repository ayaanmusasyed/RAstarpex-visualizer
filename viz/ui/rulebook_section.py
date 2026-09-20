# ui/rulebook_section.py
#
# CHANGES vs. the Streamlit-only version:
#   - st_cytoscapejs(...) -> rulebook_editor(...)   (new component, returns an event dict)
#   - added: dispatch_rulebook_event(...) + st.rerun() right after
#   - render_rulebook_selection_panel(...) call removed -- add/delete class
#     edges, merge, and split now happen in-graph. Cycle detection panel
#     is untouched since it's a passive warning, not a click target.

import streamlit as st
import pandas as pd

from viz.render.graphviz_render import dot_for_rule_class_graph
from viz.render.cytoscape_render import (
    rulebook_class_cytoscape_elements,
    rulebook_cytoscape_stylesheet,
)

from viz.core.rulebook_state import normalize_prec_df
from viz.core.rulebook_classes import default_eq_classes, class_label

from viz.ui.graph_component import rulebook_editor
from viz.ui.rulebook_dispatch import dispatch_rulebook_event
from viz.ui.rule_management_panel import render_rule_management_panel
from viz.ui.rulebook_cycle_panel import render_rulebook_cycle_panel


# Purpose:
# Render the rulebook editor section.
# Cytoscape is the main editor, while the table/Graphviz views are advanced previews.
def render_rulebook_section(rule_names):
    if "prec_df" not in st.session_state:
        st.session_state.prec_df = pd.DataFrame(
            columns=["Higher Priority", "Lower Priority"]
        )

    if "eps_values" not in st.session_state:
        st.session_state.eps_values = [0.0] * len(rule_names)

    if "eq_classes" not in st.session_state:
        st.session_state.eq_classes = default_eq_classes(rule_names)

    flat_rules = {
        rule
        for cls in st.session_state.eq_classes
        for rule in cls
    }

    if set(rule_names) != flat_rules:
        st.session_state.eq_classes = default_eq_classes(rule_names)

    st.header("Rulebook editor")

    render_rule_management_panel(
        rule_names,
        st.session_state.prec_df,
        st.session_state.eps_values,
    )

    editor_mode = st.radio(
        "Rulebook editing mode",
        ["Visual editor", "Table editor"],
        horizontal=True,
        key="rulebook_editing_mode",
    )

    prec_df = normalize_prec_df(
        st.session_state.prec_df
    )
    st.session_state.prec_df = prec_df

    if editor_mode == "Visual editor":
        st.subheader("Interactive rulebook editor")

        if not rule_names:
            st.info(
                "The rulebook is empty. Click inside the drawing "
                "area to create your first objective."
            )

        st.caption(
            "Click one class and then another to add a priority edge. "
            "Shift-click two classes to make them equivalent. "
            "Double-click a class to rename it, and right-click for "
            "more actions."
        )

        event = rulebook_editor(
            elements=rulebook_class_cytoscape_elements(
                rule_names,
                prec_df,
                st.session_state.eq_classes,
            ),
            stylesheet=rulebook_cytoscape_stylesheet(),
            key="rulebook_editor",
        )

        if event is not None:
            dispatch_rulebook_event(
                event,
                rule_names,
                prec_df,
                st.session_state.eq_classes,
            )
            st.rerun()

    else:
        st.subheader("Rulebook priority table")

        st.caption(
            "Each row represents a directed priority relationship: "
            "Higher Priority > Lower Priority. Add or remove rows to "
            "edit the rulebook."
        )

        edited_prec_df = st.data_editor(
            st.session_state.prec_df,
            key="rulebook_prec_editor",
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "Higher Priority": st.column_config.SelectboxColumn(
                    "Higher Priority",
                    options=rule_names,
                    required=True,
                ),
                "Lower Priority": st.column_config.SelectboxColumn(
                    "Lower Priority",
                    options=rule_names,
                    required=True,
                ),
            },
        )

        st.session_state.prec_df = normalize_prec_df(
            edited_prec_df
        )
        prec_df = st.session_state.prec_df

        st.subheader("Equivalence classes")

        st.caption(
            "Rules shown in the same group have equivalent priority. "
            "Use Manage rules or switch to the visual editor to merge "
            "or split groups."
        )

        if st.session_state.eq_classes:
            equivalence_rows = []

            for class_index, cls in enumerate(
                st.session_state.eq_classes
            ):
                for rule in cls:
                    equivalence_rows.append({
                        "Class": class_index,
                        "Rule": rule,
                    })

            st.dataframe(
                pd.DataFrame(equivalence_rows),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No objectives have been defined.")

    # Re-read the current rulebook after either editor modifies it.
    prec_df = normalize_prec_df(
        st.session_state.prec_df
    )
    st.session_state.prec_df = prec_df

    has_cycle = render_rulebook_cycle_panel(
        rule_names,
        prec_df,
    )

    if has_cycle:
        st.stop()

    with st.expander("Same-priority groups"):
        st.caption(
            "Rules in the same bracket are treated as "
            "equivalent priority."
        )

        if st.session_state.eq_classes:
            for i, cls in enumerate(
                st.session_state.eq_classes
            ):
                st.write(
                    f"Class {i}: `{class_label(cls)}`"
                )
        else:
            st.caption("No equivalence classes are defined.")

    with st.expander("Static rule graph preview"):
        st.caption(
            "Graphviz preview of the current rulebook state."
        )

        st.graphviz_chart(
            dot_for_rule_class_graph(
                rule_names,
                prec_df,
                st.session_state.eq_classes,
            )
        )

    return prec_df