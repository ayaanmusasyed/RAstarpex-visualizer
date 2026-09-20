// Handles mouse interactions for the visual rulebook editor.
//
// RulebookEditor owns the toolbar and selected tool. This hook owns
// Cytoscape events, pending priority edges, and equivalence selection.

import {
    useCallback,
    useEffect,
    useRef,
    useState,
  } from "react";

import { chooseRuleToDelete } from "./rulebookDelete";
  
  const PENDING_SOURCE_STYLE = {
    "border-color": "#f9a825",
    "border-width": 4,
  };
  
  
  export default function useRulebookInteractions({
    activeTool,
    onEvent,
  }) {
    const cyRef = useRef(null);
    const activeToolRef = useRef(activeTool);
    const pendingSourceRef = useRef(null);
    const equivalentSelectionRef = useRef(new Set());
  
    const [selectedCount, setSelectedCount] = useState(0);
  
  
    // Cytoscape listeners are installed once. Keep the latest selected
    // toolbar tool in a ref so those listeners always see current state.
    useEffect(() => {
      activeToolRef.current = activeTool;
    }, [activeTool]);
  
  
    // Cancel an unfinished priority edge.
    const clearPendingSource = useCallback(() => {
      if (pendingSourceRef.current) {
        pendingSourceRef.current.removeStyle(
          "border-color border-width",
        );
      }
  
      pendingSourceRef.current = null;
    }, []);
  
  
    // Clear every class selected for an equivalence merge.
    const clearEquivalentSelection = useCallback(() => {
      equivalentSelectionRef.current.clear();
      setSelectedCount(0);
  
      if (cyRef.current) {
        cyRef.current.nodes().unselect();
      }
    }, []);
  
  
    // Clear temporary selections when switching tools.
    useEffect(() => {
      if (activeTool !== "add_edge") {
        clearPendingSource();
      }
  
      if (activeTool !== "equivalent") {
        clearEquivalentSelection();
      }
    }, [
      activeTool,
      clearPendingSource,
      clearEquivalentSelection,
    ]);
  
  
    // Select or unselect one class for an equivalence merge.
    const toggleEquivalentClass = useCallback((node) => {
      const classIndex = Number(
        node.data("classIndex"),
      );
  
      const selected = equivalentSelectionRef.current;
  
      if (selected.has(classIndex)) {
        selected.delete(classIndex);
        node.unselect();
      } else {
        selected.add(classIndex);
        node.select();
      }
  
      setSelectedCount(selected.size);
    }, []);
  
  
    // Merge every class selected with the Make equivalent tool.
    const mergeSelectedClasses = useCallback(() => {
      const classIndices = Array.from(
        equivalentSelectionRef.current,
      );
  
      if (classIndices.length < 2) {
        return;
      }
  
      clearEquivalentSelection();
  
      onEvent({
        action: "merge_classes",
        class_indices: classIndices,
      });
    }, [clearEquivalentSelection, onEvent]);
  
  
    // Attach the rulebook interaction handlers to Cytoscape.
    const handleReady = useCallback(
      (cy) => {
        cyRef.current = cy;
  
        cy.on("tap", "node", (event) => {
          const node = event.target;
          const tool = activeToolRef.current;

          if (tool === "delete_rule") {
            const rules = node.data("rules") || [];
            const ruleToDelete = chooseRuleToDelete(
              rules,
            );

            if (!ruleToDelete) {
              return;
            }

            clearPendingSource();
            clearEquivalentSelection();

            onEvent({
              action: "delete_rule",
              name: ruleToDelete,
            });

            return;
          }
          
          if (tool === "equivalent") {
            toggleEquivalentClass(node);
            return;
          }
  
          if (tool !== "add_edge") {
            return;
          }
  
          // First class becomes the higher-priority source.
          if (!pendingSourceRef.current) {
            pendingSourceRef.current = node;
            node.style(PENDING_SOURCE_STYLE);
            return;
          }
  
          // Clicking the same class cancels the pending edge.
          if (pendingSourceRef.current.same(node)) {
            clearPendingSource();
            return;
          }
  
          const fromClass = pendingSourceRef.current.data(
            "classIndex",
          );
  
          const toClass = node.data("classIndex");
  
          clearPendingSource();
  
          onEvent({
            action: "add_class_edge",
            from_class: fromClass,
            to_class: toClass,
          });
        });
  
  
        // Double-click a class while using Select to rename it.
        cy.on("dbltap", "node", (event) => {
          if (activeToolRef.current !== "select") {
            return;
          }
  
          const node = event.target;
          const rules = node.data("rules") || [];
          const oldName = rules[0];
  
          if (!oldName) {
            return;
          }
  
          const newName = window.prompt(
            "Rename rule:",
            oldName,
          );
  
          if (newName && newName.trim() !== oldName) {
            onEvent({
              action: "rename_rule",
              old: oldName,
              new: newName.trim(),
            });
          }
        });
  
  
        // Empty-canvas clicks create rules while using Add rule.
        cy.on("tap", (event) => {
          if (event.target !== cy) {
            return;
          }
  
          const tool = activeToolRef.current;
  
          if (pendingSourceRef.current) {
            clearPendingSource();
            return;
          }
  
          if (tool === "equivalent") {
            clearEquivalentSelection();
            return;
          }
  
          // An entirely empty rulebook is also directly clickable.
          if (
            tool === "add_rule"
            || cy.nodes().length === 0
          ) {
            const name = window.prompt(
              "New objective name:",
            );
  
            if (name && name.trim()) {
              onEvent({
                action: "add_rule",
                name: name.trim(),
              });
            }
          }
        });
  
  
        // Context menus remain available as secondary shortcuts.
        cy.cxtmenu({
          selector: "node",
          commands: [
            {
              content: "Split into singletons",
              select: (node) => {
                clearPendingSource();
                clearEquivalentSelection();
  
                onEvent({
                  action: "split_class",
                  class_idx: node.data("classIndex"),
                });
              },
            },
          ],
        });
  
        cy.cxtmenu({
          selector: "edge",
          commands: [
            {
              content: "Delete priority edge",
              select: (edge) => {
                onEvent({
                  action: "delete_class_edge",
                  from_class: edge
                    .source()
                    .data("classIndex"),
                  to_class: edge
                    .target()
                    .data("classIndex"),
                });
              },
            },
          ],
        });
      },
      [
        clearEquivalentSelection,
        clearPendingSource,
        onEvent,
        toggleEquivalentClass,
      ],
    );
  
  
    return {
      handleReady,
      selectedCount,
      mergeSelectedClasses,
    };
  }