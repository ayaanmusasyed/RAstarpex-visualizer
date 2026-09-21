# ui/problem_graph_dispatch.py
#
# Takes one event dict back from the React problem graph editor and
# applies it to session state. All real mutations already live in
# core/problem_graph_edit.py -- this is just the lookup table.
#
# Edge actions carry "edge_index" directly (read off the cytoscape
# element's data("edge_index") in React) rather than re-finding the row
# by (source, target) strings -- matching by name broke silently on
# parallel edges and was needlessly fragile.

import streamlit as st

from viz.core.problem_graph_edit import (
    add_node,
    rename_node,
    delete_node,
    add_edge,
    update_edge,
    delete_edge,
    reverse_edge,
)


# Apply one event dict from the problem graph editor.
def dispatch_problem_graph_event(event, rule_names, start_label, goal_label):
    # Ignore empty startup values from the frontend component.
    if not isinstance(event, dict):
        return

    action = event.get("action")

    if not action:
        return

    if action == "add_node":
        node_name = str(event["name"]).strip()

        st.session_state.node_names = add_node(
            st.session_state.node_names,
            node_name,
        )

        st.session_state.setdefault(
            "node_positions",
            {},
        )

        if "x" in event and "y" in event:
            st.session_state.node_positions[node_name] = {
                "x": float(event["x"]),
                "y": float(event["y"]),
            }

        return
    
    if action == "move_node":
        node_name = str(event["name"]).strip()

        if node_name not in st.session_state.node_names:
            raise ValueError(
                f"Unknown node '{node_name}'."
            )

        st.session_state.setdefault(
            "node_positions",
            {},
        )

        st.session_state.node_positions[node_name] = {
            "x": float(event["x"]),
            "y": float(event["y"]),
        }

        return
    
    if action == "rename_node":
        old_name = str(event["old"]).strip()
        new_name = str(event["new"]).strip()

        st.session_state.node_names, st.session_state.edges_df = rename_node(
            st.session_state.node_names,
            st.session_state.edges_df,
            old_name,
            new_name,
        )

        if old_name == str(start_label).strip():
            st.session_state.pending_start_label = new_name

        if old_name == str(goal_label).strip():
            st.session_state.pending_goal_label = new_name

        positions = st.session_state.setdefault(
            "node_positions",
            {},
        )

        if old_name in positions:
            positions[new_name] = positions.pop(
                old_name
            )
        return

    if action == "delete_node":
        deleted_name = str(event["name"]).strip()

        st.session_state.node_names, st.session_state.edges_df = delete_node(
            st.session_state.node_names,
            st.session_state.edges_df,
            deleted_name,
        )

        if deleted_name == str(start_label).strip():
            st.session_state.pending_start_label = ""

        if deleted_name == str(goal_label).strip():
            st.session_state.pending_goal_label = ""

        st.session_state.setdefault(
            "node_positions",
            {},
        ).pop(
            deleted_name,
            None,
        )
        
        return

    if action == "set_start":
        st.session_state.pending_start_label = event["name"]
        return

    if action == "set_goal":
        st.session_state.pending_goal_label = event["name"]
        return

    if action == "add_edge":
        st.session_state.edges_df = add_edge(
            st.session_state.edges_df, event["source"], event["target"],
            event["costs"], len(rule_names),
        )
        return

    if action == "update_edge":
        row = st.session_state.edges_df.loc[event["edge_index"]]
        st.session_state.edges_df = update_edge(
            st.session_state.edges_df, event["edge_index"],
            row["u"], row["v"], event["costs"], len(rule_names),
        )
        return

    if action == "delete_edge":
        st.session_state.edges_df = delete_edge(
            st.session_state.edges_df, event["edge_index"],
        )
        return

    if action == "reverse_edge":
        st.session_state.edges_df = reverse_edge(
            st.session_state.edges_df, event["edge_index"],
        )
        return

    raise ValueError(f"Unknown problem graph event: {action!r}")
