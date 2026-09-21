# ui/problem_graph_section.py
#
# CHANGES vs. the Streamlit-only version:
#   - st_cytoscapejs(...) -> problem_graph_editor(...)   (new component, returns an event dict)
#   - problem_graph_editor(...) now also takes rule_names, so React can
#     label the cost-entry prompts with the actual rule order
#   - added: dispatch_problem_graph_event(...) + st.rerun() right after
#   - render_problem_graph_selection_panel(...) call removed -- its job is
#     now done in-graph by React.

import pandas as pd
import streamlit as st

from viz.core.problem_graph_state import (
    sync_edge_cost_columns,
    sync_node_names,
)
from viz.render.cytoscape_problem_graph import (
    problem_graph_cytoscape_elements,
    problem_graph_cytoscape_stylesheet,
)
from viz.ui.graph_component import problem_graph_editor
from viz.ui.problem_graph_dispatch import dispatch_problem_graph_event
from viz.ui.problem_graph_creation_panel import (
    render_problem_graph_creation_panel,
)
from viz.ui.problem_graph_sanity_check import (
    render_problem_graph_sanity_check,
)


# Render the interactive problem graph editor.
def render_problem_graph_section(
    k,
    rule_names,
    start_label,
    goal_label,
    prec_df,
    eps,
):
    initialize_problem_graph_state(
        k,
        start_label,
        goal_label,
    )

    st.header("Problem graph editor")

    render_problem_graph_creation_panel()

    editor_mode = st.radio(
        "Problem graph editing mode",
        ["Visual editor", "Table editor"],
        horizontal=True,
        key="problem_graph_editing_mode",
    )

    if editor_mode == "Visual editor":
        st.subheader("Interactive problem graph")

        st.caption(
            "Choose a tool in the graph toolbar, then click the canvas, nodes, "
            "or edges. Right-click nodes and edges for additional shortcuts."
        )

        event = problem_graph_editor(
            elements=problem_graph_cytoscape_elements(
                st.session_state.node_names,
                st.session_state.edges_df,
                rule_names,
                start_label,
                goal_label,
                st.session_state.node_positions,
            ),
            stylesheet=problem_graph_cytoscape_stylesheet(),
            rule_names=rule_names,
            key="problem_graph_editor",
        )

        if event is not None:
            dispatch_problem_graph_event(
                event,
                rule_names,
                start_label,
                goal_label,
            )
            st.rerun()

    else:
        st.subheader("Graph edge table")

        st.caption(
            "Each row represents one directed edge. Enter the source, "
            "target, and one cost for each objective."
        )

        render_edge_table(k)

    render_problem_graph_sanity_check(
        st.session_state.edges_df,
        start_label,
        goal_label,
        rule_names,
        prec_df,
        eps,
    )

    return st.session_state.edges_df

# Initialize and synchronize problem graph state.
def initialize_problem_graph_state(
    k,
    start_label,
    goal_label,
):
    if "edges_df" not in st.session_state:
        st.session_state.edges_df = pd.DataFrame(
            columns=["u", "v"]
        )

    st.session_state.edges_df = sync_edge_cost_columns(st.session_state.edges_df, k,)

    if "node_names" not in st.session_state:
        st.session_state.node_names = []

    st.session_state.node_names = sync_node_names(st.session_state.node_names, st.session_state.edges_df, start_label, goal_label,)

    if "node_positions" not in st.session_state:
        st.session_state.node_positions = {}

    # Remove positions belonging to nodes that no longer exist.
    st.session_state.node_positions = {
        node: position
        for node, position
        in st.session_state.node_positions.items()
        if node in st.session_state.node_names
    }

# Render the editable edge table as an advanced option.
# Left as plain Streamlit on purpose -- typing exact float costs is
# fiddly on a canvas. This is the power-user fallback for bulk edits.
def render_edge_table(k):
    column_config = {
        "u": st.column_config.TextColumn(
            "Source",
            required=True,
        ),
        "v": st.column_config.TextColumn(
            "Target",
            required=True,
        ),
    }

    for i in range(k):
        column_config[f"c{i}"] = (
            st.column_config.NumberColumn(
                f"Objective {i}",
                min_value=0.0,
                step=1.0,
                required=True,
            )
        )

    edited_edges = st.data_editor(
        st.session_state.edges_df,
        key="problem_edges_editor",
        use_container_width=True,
        num_rows="dynamic",
        column_config=column_config,
    )

    st.session_state.edges_df = sync_edge_cost_columns(
        edited_edges,
        k,
    )

    st.session_state.node_names = sync_node_names(
        st.session_state.node_names,
        st.session_state.edges_df,
        st.session_state.get("start_label", ""),
        st.session_state.get("goal_label", ""),
    )