import streamlit as st

from viz.core.rulebook_classes import remove_edges_inside_classes

from viz.core.rulebook_state import rename_rule
from viz.core.rulebook_edit import (
    add_class_edge,
    delete_class_edge,
    merge_class_indices,
    split_equivalence_class,
)

from viz.core.rule_management import (
    add_rule,
    delete_rule,
)
from viz.core.problem_graph_state import sync_edge_cost_columns

# Apply one event dict from the rulebook editor.
def dispatch_rulebook_event(event, rule_names, prec_df, eq_classes):
    action = event.get("action")
    if action == "add_rule":
        current_eps = list(
            st.session_state.get("eps_values", [])
        )

        # Keep epsilon aligned with the current rule list before appending
        # the new objective.
        current_eps = current_eps[:len(rule_names)]

        if len(current_eps) < len(rule_names):
            current_eps.extend(
                [0.0] * (len(rule_names) - len(current_eps))
            )

        new_rule_names, new_eq_classes, new_eps = add_rule(
            rule_names,
            eq_classes,
            current_eps,
            event["name"],
        )

        st.session_state.eq_classes = new_eq_classes

        # These values are applied before the sidebar widgets are rendered
        # on the following Streamlit rerun.
        st.session_state.pending_rule_names_csv = ",".join(
            new_rule_names
        )
        st.session_state.pending_eps_values = new_eps
        st.session_state.pending_k = len(new_rule_names)

        # Add the new objective's cost column to existing graph edges.
        if "edges_df" in st.session_state:
            st.session_state.edges_df = sync_edge_cost_columns(
                st.session_state.edges_df,
                len(new_rule_names),
            )

        return
    if action == "delete_rule":
        current_eps = list(
            st.session_state.get("eps_values", [])
        )

        # Keep epsilon values aligned with the rule list.
        current_eps = current_eps[:len(rule_names)]

        if len(current_eps) < len(rule_names):
            current_eps.extend(
                [0.0] * (len(rule_names) - len(current_eps))
            )

        (
            new_rule_names,
            new_eq_classes,
            new_prec_df,
            new_eps,
        ) = delete_rule(
            rule_names,
            eq_classes,
            prec_df,
            current_eps,
            event["name"],
        )

        st.session_state.eq_classes = new_eq_classes
        st.session_state.prec_df = new_prec_df

        st.session_state.pending_rule_names_csv = ",".join(
            new_rule_names
        )
        st.session_state.pending_eps_values = new_eps
        st.session_state.pending_k = len(new_rule_names)

        # Remove the deleted objective's graph cost column.
        if "edges_df" in st.session_state:
            st.session_state.edges_df = sync_edge_cost_columns(
                st.session_state.edges_df,
                len(new_rule_names),
            )

        return
    
    if action == "rename_rule":
        old_name = str(event["old"]).strip()
        new_name = str(event["new"]).strip()

        new_rule_names, new_prec_df = rename_rule(
            rule_names,
            prec_df,
            old_name,
            new_name,
        )

        new_eq_classes = [
            [
                new_name if rule == old_name else rule
                for rule in cls
            ]
            for cls in eq_classes
        ]

        st.session_state.pending_rule_names_csv = ",".join(
            new_rule_names
        )
        st.session_state.eq_classes = new_eq_classes
        st.session_state.prec_df = new_prec_df
        return

    if action == "add_class_edge":
        st.session_state.prec_df = add_class_edge(
            prec_df, eq_classes, event["from_class"], event["to_class"],
        )
        return

    if action == "delete_class_edge":
        st.session_state.prec_df = delete_class_edge(
            prec_df, eq_classes, event["from_class"], event["to_class"],
        )
        return

    if action == "merge_classes":
        new_eq_classes = merge_class_indices(
            eq_classes,
            event["class_indices"],
        )

        st.session_state.eq_classes = new_eq_classes
        st.session_state.prec_df = remove_edges_inside_classes(
            prec_df,
            new_eq_classes,
        )
        return

    if action == "split_class":
        st.session_state.eq_classes = split_equivalence_class(
            eq_classes, event["class_idx"],
        )
        return

    raise ValueError(f"Unknown rulebook event: {action!r}")
