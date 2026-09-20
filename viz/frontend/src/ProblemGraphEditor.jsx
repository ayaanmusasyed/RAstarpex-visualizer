// ProblemGraphEditor.jsx
//
// Interaction model:
//   - tap an empty spot on the canvas       -> add a new node
//   - tap a node once                        -> mark it as the pending edge source (highlighted)
//   - tap a second, different node            -> completes the edge: prompts for costs, emits add_edge
//   - tap the same node again                 -> cancels the pending edge
//   - tap empty canvas while a source pending -> cancels the pending edge (does NOT add a node)
//   - double-click a node                     -> rename
//   - tap an edge                             -> edit its costs
//   - right-click a node                      -> set start / set goal / delete
//   - right-click an edge                     -> reverse / delete
//
// IMPORTANT: cytoscape node ids are "node::<name>" (see
// render/cytoscape_problem_graph.py), the real name lives in
// data("node_name"). Edge ids are "edge::<edge_index>", the real row
// index lives in data("edge_index"). Always read the *_name / edge_index
// fields, never .id(), when building an event -- using .id() directly
// was the earlier bug that made delete/rename/reverse silently fail.

// Visual toolbar for editing the problem graph.
//
// The graph elements and styling still come from Python.
// This file only owns the toolbar and connects it to the
// Cytoscape interaction hook.

import React, { useState } from "react";

import EditorToolbar from "./EditorToolbar";
import GraphCanvas from "./GraphCanvas";
import useProblemGraphInteractions from "./useProblemGraphInteractions";


const PROBLEM_GRAPH_TOOLS = [
  {
    id: "select",
    label: "Select",
    help: "Drag nodes or double-click one to rename it.",
  },
  {
    id: "add_node",
    label: "Add node",
    help: "Click empty canvas space to add a node.",
  },
  {
    id: "add_edge",
    label: "Add edge",
    help: "Click the source node, then the destination node.",
  },
  {
    id: "edit_costs",
    label: "Edit costs",
    help: "Click an edge to change its costs.",
  },
  {
    id: "set_start",
    label: "Set start",
    help: "Click a node to make it the start node.",
  },
  {
    id: "set_goal",
    label: "Set goal",
    help: "Click a node to make it the goal node.",
  },
  {
    id: "reverse_edge",
    label: "Reverse",
    help: "Click an edge to reverse its direction.",
  },
  {
    id: "delete",
    label: "Delete",
    help: "Click a node or edge to delete it.",
  },
];


const TOOL_HELP = {
  select:
    "Select mode: drag nodes or double-click one to rename it.",

  add_node:
    "Add node mode: click empty canvas space to create a node.",

  add_edge:
    "Add edge mode: click the source node first, then the destination node.",

  edit_costs:
    "Edit costs mode: click an edge and enter one cost for each objective.",

  set_start:
    "Set start mode: click the node that should be used as the start.",

  set_goal:
    "Set goal mode: click the node that should be used as the goal.",

  reverse_edge:
    "Reverse mode: click an edge to reverse its direction.",

  delete:
    "Delete mode: click a node or edge to remove it.",
};


export default function ProblemGraphEditor({
  elements,
  stylesheet,
  ruleNames,
  onEvent,
}) {
  const [activeTool, setActiveTool] = useState("select");

  const {
    handleReady,
    clearPendingSource,
  } = useProblemGraphInteractions({
    activeTool,
    ruleNames,
    onEvent,
  });


  const toolbar = (
    <>
      <EditorToolbar
        tools={PROBLEM_GRAPH_TOOLS}
        activeTool={activeTool}
        onToolChange={(tool) => {
          clearPendingSource();
          setActiveTool(tool);
        }}
      />

      <div className="editor-tool-help">
        {TOOL_HELP[activeTool]}
      </div>
    </>
  );


  return (
    <GraphCanvas
      elements={elements}
      stylesheet={stylesheet}
      layout={{
        name: "preset",
        fit: true,
        padding: 45,
      }}
      onReady={handleReady}
      toolbar={toolbar}
    />
  );
}