// Ask which rule should be deleted from a rulebook class.

export function chooseRuleToDelete(rules) {
    if (!Array.isArray(rules) || rules.length === 0) {
      return null;
    }
  
    let selectedRule = rules[0];
  
    // A class may contain several equivalent rules.
    if (rules.length > 1) {
      const answer = window.prompt(
        `Which rule should be deleted?\n${rules.join(", ")}`,
        rules[0],
      );
  
      if (!answer) {
        return null;
      }
  
      selectedRule = answer.trim();
  
      if (!rules.includes(selectedRule)) {
        window.alert(
          `"${selectedRule}" is not in this equivalence class.`,
        );
  
        return null;
      }
    }
  
    const confirmed = window.confirm(
      `Delete rule "${selectedRule}"?\n\n` +
        "Its epsilon value, graph cost column, and connected " +
        "priority relationships will also be removed.",
    );
  
    return confirmed ? selectedRule : null;
  }