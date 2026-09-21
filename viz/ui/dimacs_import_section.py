# Streamlit controls for importing DIMACS .gr objective files.

import streamlit as st

from viz.core.dimacs_gr import (
    parse_dimacs_gr_bundle,
)


def render_dimacs_import_section():
    with st.expander("Import DIMACS .gr files"):
        st.caption(
            "Upload one .gr file per objective. All files must "
            "contain the same arcs in the same order. The upload "
            "order determines the cost-vector order."
        )

        uploaded_files = st.file_uploader(
            "DIMACS objective files",
            type=["gr"],
            accept_multiple_files=True,
            key="dimacs_gr_files",
        )

        default_names = ""

        if uploaded_files:
            default_names = ",".join(
                uploaded_file.name.removesuffix(".gr")
                for uploaded_file in uploaded_files
            )

        rule_names_text = st.text_input(
            "Objective names, comma-separated",
            value=default_names,
            key="dimacs_rule_names",
        )

        c1, c2 = st.columns(2)

        start = c1.text_input(
            "Start node ID",
            value="1",
            key="dimacs_start",
        )

        goal = c2.text_input(
            "Goal node ID",
            key="dimacs_goal",
        )

        if st.button(
            "Load DIMACS graph",
            key="load_dimacs_graph",
        ):
            try:
                rule_names = [
                    name.strip()
                    for name in rule_names_text.split(",")
                    if name.strip()
                ]

                parsed = parse_dimacs_gr_bundle(
                    uploaded_files,
                    start,
                    goal,
                    rule_names or None,
                )

                old_k = st.session_state.get(
                    "k",
                    len(parsed["rule_names"]),
                )

                st.session_state.k = len(
                    parsed["rule_names"]
                )

                st.session_state.rule_names_csv = ",".join(
                    parsed["rule_names"]
                )

                st.session_state.eps_values = parsed["eps"]
                st.session_state.eq_classes = parsed["eq_classes"]
                st.session_state.prec_df = parsed["prec_df"]
                st.session_state.node_names = parsed["node_names"]
                st.session_state.node_positions = {}
                st.session_state.edges_df = parsed["edges_df"]
                st.session_state.start_label = parsed["start"]
                st.session_state.goal_label = parsed["goal"]

                for index, value in enumerate(
                    parsed["eps"]
                ):
                    st.session_state[f"eps_{index}"] = float(
                        value
                    )

                for index in range(
                    len(parsed["rule_names"]),
                    old_k,
                ):
                    st.session_state.pop(
                        f"eps_{index}",
                        None,
                    )

                st.success(
                    f"Loaded {len(parsed['node_names'])} nodes, "
                    f"{len(parsed['edges_df'])} arcs, and "
                    f"{len(parsed['rule_names'])} objectives."
                )

                st.rerun()

            except Exception as error:
                st.warning(str(error))