// Mouse interactions for the visual problem graph toolbar.

import {
    useCallback,
    useEffect,
    useRef,
  } from "react";
  
  import {
    formatProblemGraphCosts,
    parseProblemGraphCosts,
  } from "./problemGraphCosts";
  
  
  const PENDING_SOURCE_STYLE = {
    "border-color": "#f9a825",
    "border-width": 4,
  };
  
  
  export default function useProblemGraphInteractions({
    activeTool,
    ruleNames,
    onEvent,
  }) {
    const activeToolRef = useRef(activeTool);
    const ruleNamesRef = useRef(ruleNames);
    const onEventRef = useRef(onEvent);
    const pendingSourceRef = useRef(null);
    const dragStartRef = useRef(null);
  
    useEffect(() => {
      activeToolRef.current = activeTool;
    }, [activeTool]);
  
    useEffect(() => {
      ruleNamesRef.current = ruleNames;
    }, [ruleNames]);
  
    useEffect(() => {
      onEventRef.current = onEvent;
    }, [onEvent]);
  
  
    const clearPendingSource = useCallback(() => {
      if (pendingSourceRef.current) {
        pendingSourceRef.current.removeStyle(
          "border-color border-width",
        );
      }
  
      pendingSourceRef.current = null;
    }, []);
  
  
    useEffect(() => {
      if (activeTool !== "add_edge") {
        clearPendingSource();
      }
    }, [activeTool, clearPendingSource]);
  
  
    const askForCosts = useCallback((currentCosts = []) => {
      const names = ruleNamesRef.current;
  
      if (names.length === 0) {
        window.alert(
          "Add at least one objective before adding an edge.",
        );
  
        return null;
      }
  
      const rawCosts = window.prompt(
        `Enter costs in this order: ${names.join(", ")}`,
        formatProblemGraphCosts(currentCosts),
      );
  
      return parseProblemGraphCosts(rawCosts, names);
    }, []);
  
  
    const handleReady = useCallback(
      (cy) => {
        // Remember where a node started before dragging.
        cy.on("grab", "node", (event) => {
          if (activeToolRef.current !== "select") {
            dragStartRef.current = null;
            return;
          }

          const node = event.target;
          const position = node.position();

          dragStartRef.current = {
            nodeName: node.data("node_name"),
            x: position.x,
            y: position.y,
          };
        });


        // Save a node position only if it actually moved.
        cy.on("free", "node", (event) => {
          const start = dragStartRef.current;
          dragStartRef.current = null;

          if (!start) {
            return;
          }

          const node = event.target;
          const position = node.position();

          const moved =
            Math.abs(position.x - start.x) > 0.5
            || Math.abs(position.y - start.y) > 0.5;

          if (!moved) {
            return;
          }

          onEventRef.current({
            action: "move_node",
            name: node.data("node_name"),
            x: position.x,
            y: position.y,
          });
        });


        // Handle node tools.
        cy.on("tap", "node", (event) => {
          const node = event.target;
          const nodeName = node.data("node_name");
          const tool = activeToolRef.current;
  
  
          if (tool === "add_edge") {
            const sourceNode = pendingSourceRef.current;
  
            if (!sourceNode) {
              pendingSourceRef.current = node;
              node.style(PENDING_SOURCE_STYLE);
              return;
            }
  
            if (sourceNode.same(node)) {
              clearPendingSource();
              return;
            }
  
            const sourceName = sourceNode.data(
              "node_name",
            );
  
            const costs = askForCosts();
  
            clearPendingSource();
  
            if (costs === null) {
              return;
            }
  
            onEventRef.current({
              action: "add_edge",
              source: sourceName,
              target: nodeName,
              costs,
            });
  
            return;
          }
  
  
          if (tool === "set_start") {
            onEventRef.current({
              action: "set_start",
              name: nodeName,
            });
  
            return;
          }
  
  
          if (tool === "set_goal") {
            onEventRef.current({
              action: "set_goal",
              name: nodeName,
            });
  
            return;
          }
  
  
          if (tool === "delete") {
            onEventRef.current({
              action: "delete_node",
              name: nodeName,
            });
          }
        });
  
  
        // Handle edge tools.
        cy.on("tap", "edge", (event) => {
          const edge = event.target;
          const edgeIndex = edge.data("edge_index");
          const tool = activeToolRef.current;
  
  
          if (tool === "edit_costs") {
            const costs = askForCosts(
              edge.data("costs") || [],
            );
  
            if (costs !== null) {
              onEventRef.current({
                action: "update_edge",
                edge_index: edgeIndex,
                costs,
              });
            }
  
            return;
          }
  
  
          if (tool === "reverse_edge") {
            onEventRef.current({
              action: "reverse_edge",
              edge_index: edgeIndex,
            });
  
            return;
          }
  
  
          if (tool === "delete") {
            onEventRef.current({
              action: "delete_edge",
              edge_index: edgeIndex,
            });
          }
        });
  
  
        // Add nodes by clicking empty canvas space.
        cy.on("tap", (event) => {
          if (event.target !== cy) {
            return;
          }
  
          if (pendingSourceRef.current) {
            clearPendingSource();
            return;
          }
  
          if (activeToolRef.current !== "add_node") {
            return;
          }
  
          const name = window.prompt("New node name:");
  
          if (!name || !name.trim()) {
            return;
          }
  
          onEventRef.current({
            action: "add_node",
            name: name.trim(),
            x: event.position.x,
            y: event.position.y,
          });
        });
  
  
        // Rename nodes in Select mode.
        cy.on("dbltap", "node", (event) => {
          if (activeToolRef.current !== "select") {
            return;
          }
  
          const node = event.target;
          const oldName = node.data("node_name");
  
          const newName = window.prompt(
            "Rename node:",
            oldName,
          );
  
          if (
            !newName
            || !newName.trim()
            || newName.trim() === oldName
          ) {
            return;
          }
  
          onEventRef.current({
            action: "rename_node",
            old: oldName,
            new: newName.trim(),
          });
        });
      },
      [
        askForCosts,
        clearPendingSource,
      ],
    );
  
  
    return {
      handleReady,
      clearPendingSource,
    };
  }