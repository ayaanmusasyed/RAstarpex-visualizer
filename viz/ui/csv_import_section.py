# Controls for importing a multi-objective CSV edge list.

import streamlit as st

from viz.core.csv_problem import (
    parse_problem_csv,
)


def render_csv_import_section():
    with st.expander("Import CSV edge list"):
        st.caption(
            "Use source and target columns followed by one "
            "cost column per objective. Start and goal are "
            "detected automatically when the graph has one "
            "clear source and one clear sink."
        )

        st.code(
            "source,target,distance,energy\n"
            "S,A,4,8\n"
            "A,T,3,2",
            language="csv",
        )

        uploaded_csv = st.file_uploader(
            "CSV graph",
            type=["csv"],
            key="problem_csv",
        )

        c1, c2 = st.columns(2)

        start = c1.text_input(
            "Start node override",
            help=(
                "Leave blank to detect it automatically."
            ),
            key="csv_start",
        )

        goal = c2.text_input(
            "Goal node override",
            help=(
                "Leave blank to detect it automatically."
            ),
            key="csv_goal",
        )

        if st.button(
            "Load CSV graph",
            key="load_csv_graph",
        ):
            try:
                if uploaded_csv is None:
                    raise ValueError(
                        "Upload a CSV file first."
                    )

                raw_csv = uploaded_csv.getvalue().decode(
                    "utf-8"
                )

                parsed = parse_problem_csv(
                    raw_csv,
                    start,
                    goal,
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
                    f"{len(parsed['edges_df'])} edges, and "
                    f"{len(parsed['rule_names'])} objectives."
                )

                st.rerun()

            except Exception as error:
                st.warning(str(error))