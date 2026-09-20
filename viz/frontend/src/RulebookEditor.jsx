// RulebookEditor.jsx
//
// Interaction model (mirrors ProblemGraphEditor.jsx):
//   - tap a class once            -> mark it as the pending edge source (highlighted)
//   - tap a second, different class -> completes a priority edge, emits add_class_edge
//   - tap the same class again     -> cancels the pending edge
//   - tap empty canvas while pending -> cancels the pending edge
//   - shift-click two classes      -> merge them (unrelated to the pending-edge state)
//   - double-click a class         -> rename its representative rule
//   - right-click a class          -> split into singletons
//   - right-click a priority edge  -> delete it
//
// Class node ids are "class_<i>" and already carry a clean "classIndex"
// field (added in render/cytoscape_render.py) -- no id-prefix bug here
// the way the problem graph had.

import React, { useState } from "react";

import EditorToolbar from "./EditorToolbar";
import GraphCanvas from "./GraphCanvas";
import useRulebookInteractions from "./useRulebookInteractions";


const RULEBOOK_TOOLS = [
  {
    id: "select",
    label: "Select",
    help: "Select, move, or double-click a class to rename it.",
  },
  {
    id: "add_rule",
    label: "Add rule",
    help: "Click empty canvas space to create a new objective.",
  },
  {
    id: "add_edge",
    label: "Add priority",
    help: "Click the higher-priority class, then the lower-priority class.",
  },
  {
    id: "equivalent",
    label: "Make equivalent",
    help: "Select two or more classes, then merge them.",
  },
];


const TOOL_HELP = {
  select:
    "Select mode: drag classes or double-click one to rename it.",

  add_rule:
    "Add rule mode: click empty canvas space to create an objective.",

  add_edge:
    "Add priority mode: click the higher-priority class first, then the lower-priority class.",

  equivalent:
    "Make equivalent mode: click two or more classes, then press Merge selected.",
};


export default function RulebookEditor({
  elements,
  stylesheet,
  onEvent,
}) {
  const [activeTool, setActiveTool] = useState(
    "select",
  );

  const {
    handleReady,
    selectedCount,
    mergeSelectedClasses,
  } = useRulebookInteractions({
    activeTool,
    onEvent,
  });


  const actions = [];

  if (activeTool === "equivalent") {
    actions.push({
      id: "merge_selected",
      label: `Merge selected (${selectedCount})`,
      disabled: selectedCount < 2,
      onClick: mergeSelectedClasses,
    });
  }


  const toolbar = (
    <>
      <EditorToolbar
        tools={RULEBOOK_TOOLS}
        activeTool={activeTool}
        onToolChange={setActiveTool}
        actions={actions}
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
        name: "dagre",
        animate: false,
      }}
      onReady={handleReady}
      toolbar={toolbar}
    />
  );
}