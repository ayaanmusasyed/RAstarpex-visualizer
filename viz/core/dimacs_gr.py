# Parse one or more DIMACS shortest-path .gr files.
#
# Each file supplies one objective. Every file must describe
# the same nodes and arcs in the same order.

from pathlib import Path

import pandas as pd


def parse_dimacs_gr_file(filename, text):
    node_count = None
    expected_arc_count = None
    arcs = []

    for line_number, raw_line in enumerate(
        text.splitlines(),
        start=1,
    ):
        line = raw_line.strip()

        if not line or line.startswith("c"):
            continue

        parts = line.split()
        line_type = parts[0]


        if line_type == "p":
            if len(parts) != 4 or parts[1] != "sp":
                raise ValueError(
                    f"{filename}, line {line_number}: "
                    "expected 'p sp <nodes> <arcs>'."
                )

            if node_count is not None:
                raise ValueError(
                    f"{filename}: more than one problem line."
                )

            node_count = int(parts[2])
            expected_arc_count = int(parts[3])
            continue


        if line_type == "a":
            if node_count is None:
                raise ValueError(
                    f"{filename}, line {line_number}: "
                    "the problem line must appear before arcs."
                )

            if len(parts) != 4:
                raise ValueError(
                    f"{filename}, line {line_number}: "
                    "expected 'a <source> <target> <weight>'."
                )

            source = int(parts[1])
            target = int(parts[2])
            weight = int(parts[3])

            if not 1 <= source <= node_count:
                raise ValueError(
                    f"{filename}, line {line_number}: "
                    f"source node {source} is outside 1..{node_count}."
                )

            if not 1 <= target <= node_count:
                raise ValueError(
                    f"{filename}, line {line_number}: "
                    f"target node {target} is outside 1..{node_count}."
                )

            # DIMACS technically permits signed weights, but the
            # current RA*pex interface expects nonnegative costs.
            if weight < 0:
                raise ValueError(
                    f"{filename}, line {line_number}: "
                    "negative weights are not currently supported."
                )

            arcs.append((source, target, weight))
            continue


        raise ValueError(
            f"{filename}, line {line_number}: "
            f"unsupported line type '{line_type}'."
        )


    if node_count is None:
        raise ValueError(
            f"{filename}: missing 'p sp <nodes> <arcs>' line."
        )

    if len(arcs) != expected_arc_count:
        raise ValueError(
            f"{filename}: header declares "
            f"{expected_arc_count} arcs, but {len(arcs)} were found."
        )

    return {
        "filename": filename,
        "node_count": node_count,
        "arcs": arcs,
    }


def parse_dimacs_gr_bundle(
    uploaded_files,
    start,
    goal,
    rule_names=None,
):
    if not uploaded_files:
        raise ValueError(
            "Upload at least one DIMACS .gr file."
        )

    parsed_files = []

    for uploaded_file in uploaded_files:
        try:
            text = uploaded_file.getvalue().decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError(
                f"{uploaded_file.name} is not valid UTF-8 text."
            ) from error

        parsed_files.append(
            parse_dimacs_gr_file(
                uploaded_file.name,
                text,
            )
        )


    first = parsed_files[0]
    node_count = first["node_count"]

    reference_topology = [
        (source, target)
        for source, target, _ in first["arcs"]
    ]


    # Every objective must describe the same graph.
    for parsed in parsed_files[1:]:
        if parsed["node_count"] != node_count:
            raise ValueError(
                f"{parsed['filename']} has "
                f"{parsed['node_count']} nodes, but "
                f"{first['filename']} has {node_count}."
            )

        topology = [
            (source, target)
            for source, target, _ in parsed["arcs"]
        ]

        if topology != reference_topology:
            raise ValueError(
                f"{parsed['filename']} does not have the same "
                "arcs in the same order as the first objective file."
            )


    if rule_names is None:
        rule_names = [
            Path(parsed["filename"]).stem
            for parsed in parsed_files
        ]

    rule_names = [
        str(name).strip()
        for name in rule_names
    ]

    if len(rule_names) != len(parsed_files):
        raise ValueError(
            "Provide exactly one rule name per .gr file."
        )

    if any(not name for name in rule_names):
        raise ValueError(
            "Rule names cannot be empty."
        )

    if len(set(rule_names)) != len(rule_names):
        raise ValueError(
            "Rule names must be unique."
        )


    start = str(start).strip()
    goal = str(goal).strip()

    if not start or not goal:
        raise ValueError(
            "Start and goal node IDs are required."
        )

    try:
        start_id = int(start)
        goal_id = int(goal)
    except ValueError as error:
        raise ValueError(
            "DIMACS start and goal must be integer node IDs."
        ) from error

    if not 1 <= start_id <= node_count:
        raise ValueError(
            f"Start node must be between 1 and {node_count}."
        )

    if not 1 <= goal_id <= node_count:
        raise ValueError(
            f"Goal node must be between 1 and {node_count}."
        )


    rows = []

    for edge_index, (source, target) in enumerate(
        reference_topology
    ):
        row = {
            "u": str(source),
            "v": str(target),
        }

        for objective_index, parsed in enumerate(
            parsed_files
        ):
            row[f"c{objective_index}"] = float(
                parsed["arcs"][edge_index][2]
            )

        rows.append(row)


    edge_columns = [
        "u",
        "v",
        *[
            f"c{i}"
            for i in range(len(rule_names))
        ],
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
        "node_names": [
            str(node_id)
            for node_id in range(1, node_count + 1)
        ],
        "edges_df": pd.DataFrame(
            rows,
            columns=edge_columns,
        ),
        "start": str(start_id),
        "goal": str(goal_id),
        "eps": [0.0] * len(rule_names),
    }