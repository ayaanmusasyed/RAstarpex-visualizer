// Shared toolbar used by the visual graph editors.
//
// Each editor supplies its own tools and actions. This component only
// handles presentation and active-tool selection.

import React from "react";

export default function EditorToolbar({
  tools,
  activeTool,
  onToolChange,
  actions = [],
}) {
  return (
    <div className="editor-toolbar">
      <div className="editor-toolbar-tools">
        {tools.map((tool) => (
          <button
            key={tool.id}
            type="button"
            className={
              activeTool === tool.id
                ? "editor-tool-button active"
                : "editor-tool-button"
            }
            onClick={() => onToolChange(tool.id)}
            title={tool.help}
          >
            {tool.label}
          </button>
        ))}
      </div>

      {actions.length > 0 && (
        <div className="editor-toolbar-actions">
          {actions.map((action) => (
            <button
              key={action.id}
              type="button"
              className="editor-action-button"
              onClick={action.onClick}
              disabled={action.disabled}
            >
              {action.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}