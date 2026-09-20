# Parse a multi-objective graph from one CSV edge-list file.

from io import StringIO

import pandas as pd


SOURCE_NAMES = {"source", "u", "from"}
TARGET_NAMES = {"target", "v", "to"}


def find_column(columns, accepted_names):
    for column in columns:
        if column.strip().lower() in accepted_names:
            return column

    return None


def infer_start_goal(node_names, edges_df):
    sources = set(edges_df["u"])
    targets = set(edges_df["v"])

    possible_starts = [
        node for node in node_names
        if node in sources and node not in targets
    ]

    possible_goals = [
        node for node in node_names
        if node in targets and node not in sources
    ]

    start = (
        possible_starts[0]
        if len(possible_starts) == 1
        else None
    )

    goal = (
        possible_goals[0]
        if len(possible_goals) == 1
        else None
    )

    return start, goal


def parse_problem_csv(
    raw_csv,
    requested_start="",
    requested_goal="",
):
    try:
        source_df = pd.read_csv(
            StringIO(raw_csv)
        )
    except Exception as error:
        raise ValueError(
            f"Could not read CSV: {error}"
        ) from error

    if source_df.empty:
        raise ValueError(
            "The CSV does not contain any graph edges."
        )

    source_column = find_column(
        source_df.columns,
        SOURCE_NAMES,
    )

    target_column = find_column(
        source_df.columns,
        TARGET_NAMES,
    )

    if source_column is None:
        raise ValueError(
            "The CSV needs a source column named "
            "'source', 'u', or 'from'."
        )

    if target_column is None:
        raise ValueError(
            "The CSV needs a target column named "
            "'target', 'v', or 'to'."
        )

    objective_columns = [
        column
        for column in source_df.columns
        if column not in {
            source_column,
            target_column,
        }
    ]

    if not objective_columns:
        raise ValueError(
            "The CSV needs at least one objective cost column."
        )


    rows = []

    for row_index, source_row in source_df.iterrows():
        source = str(
            source_row[source_column]
        ).strip()

        target = str(
            source_row[target_column]
        ).strip()

        if not source or source.lower() == "nan":
            raise ValueError(
                f"Row {row_index + 2} has no source node."
            )

        if not target or target.lower() == "nan":
            raise ValueError(
                f"Row {row_index + 2} has no target node."
            )

        row = {
            "u": source,
            "v": target,
        }

        for objective_index, column in enumerate(
            objective_columns
        ):
            try:
                cost = float(source_row[column])
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"Row {row_index + 2}, column "
                    f"'{column}' is not numeric."
                ) from error

            if pd.isna(cost) or cost < 0:
                raise ValueError(
                    f"Row {row_index + 2}, column "
                    f"'{column}' must be nonnegative."
                )

            row[f"c{objective_index}"] = cost

        rows.append(row)


    edges_df = pd.DataFrame(rows)

    node_names = []

    for row in rows:
        for node in [row["u"], row["v"]]:
            if node not in node_names:
                node_names.append(node)


    inferred_start, inferred_goal = infer_start_goal(
        node_names,
        edges_df,
    )

    start = (
        str(requested_start).strip()
        or inferred_start
    )

    goal = (
        str(requested_goal).strip()
        or inferred_goal
    )

    if not start:
        raise ValueError(
            "Start node could not be inferred. "
            "Enter it manually."
        )

    if not goal:
        raise ValueError(
            "Goal node could not be inferred. "
            "Enter it manually."
        )

    if start not in node_names:
        raise ValueError(
            f"Start node '{start}' is not in the graph."
        )

    if goal not in node_names:
        raise ValueError(
            f"Goal node '{goal}' is not in the graph."
        )


    rule_names = [
        str(column).strip()
        for column in objective_columns
    ]

    return {
        "rule_names": rule_names,
        "eq_classes": [
            [rule]
            for rule in rule_names
        ],
        "prec_df": pd.DataFrame(
            columns=[
                "Higher Priority",
                "Lower Priority",
            ]
        ),
        "node_names": node_names,
        "edges_df": edges_df,
        "start": start,
        "goal": goal,
        "eps": [0.0] * len(rule_names),
    }