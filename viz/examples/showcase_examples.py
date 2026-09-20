SHOWCASE_EXAMPLES = {
    "Showcase: dominated path pruning": """{
  "rules": ["distance", "risk"],
  "rulebook": {
    "classes": [["distance"], ["risk"]],
    "edges": [["distance", "risk"]]
  },
  "graph": {
    "edges": [
      {"u": "S", "v": "A", "c": [1, 1]},
      {"u": "A", "v": "M", "c": [1, 1]},

      {"u": "S", "v": "B", "c": [2, 3]},
      {"u": "B", "v": "M", "c": [2, 3]},

      {"u": "M", "v": "T", "c": [1, 1]}
    ]
  },
  "start": "S",
  "goal": "T",
  "eps": [0, 0]
}""",

    "Showcase: epsilon approximation": """{
  "rules": ["time", "energy"],
  "rulebook": {
    "classes": [["time"], ["energy"]],
    "edges": []
  },
  "graph": {
    "edges": [
      {"u": "S", "v": "A", "c": [5, 5]},
      {"u": "A", "v": "M", "c": [5, 5]},

      {"u": "S", "v": "B", "c": [5.25, 4.8]},
      {"u": "B", "v": "M", "c": [5.25, 4.8]},

      {"u": "M", "v": "T", "c": [1, 1]}
    ]
  },
  "start": "S",
  "goal": "T",
  "eps": [0.1, 0.1]
}""",

    "Showcase: equivalence classes": """{
  "rules": ["safety", "time", "energy"],
  "rulebook": {
    "classes": [
      ["safety"],
      ["time", "energy"]
    ],
    "edges": [
      ["safety", "time"],
      ["safety", "energy"]
    ]
  },
  "graph": {
    "edges": [
      {"u": "S", "v": "Safe", "c": [1, 5, 6]},
      {"u": "Safe", "v": "T", "c": [1, 5, 6]},

      {"u": "S", "v": "Fast", "c": [3, 2, 5]},
      {"u": "Fast", "v": "T", "c": [3, 2, 5]},

      {"u": "S", "v": "Efficient", "c": [3, 5, 2]},
      {"u": "Efficient", "v": "T", "c": [3, 5, 2]}
    ]
  },
  "start": "S",
  "goal": "T",
  "eps": [0, 0, 0]
}""",

    "Showcase: partial-order tradeoffs": """{
  "rules": ["safety", "time", "energy", "toll"],
  "rulebook": {
    "classes": [
      ["safety"],
      ["time"],
      ["energy"],
      ["toll"]
    ],
    "edges": [
      ["safety", "time"],
      ["safety", "energy"]
    ]
  },
  "graph": {
    "edges": [
      {"u": "S", "v": "A", "c": [1, 7, 7, 8]},
      {"u": "A", "v": "T", "c": [1, 7, 7, 8]},

      {"u": "S", "v": "B", "c": [2, 3, 3, 1]},
      {"u": "B", "v": "T", "c": [2, 3, 3, 1]},

      {"u": "S", "v": "C", "c": [1, 9, 2, 4]},
      {"u": "C", "v": "T", "c": [1, 9, 2, 4]}
    ]
  },
  "start": "S",
  "goal": "T",
  "eps": [0, 0, 0, 0]
}""",
}