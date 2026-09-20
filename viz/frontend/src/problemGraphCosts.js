// Check the costs before sending them back to Streamlit.

export function parseProblemGraphCosts(rawCosts, ruleNames) {
    if (rawCosts === null) {
      return null;
    }
  
    const parts = rawCosts.split(",").map((value) => value.trim());
    const costs = parts.map(Number);
  
    const wrongNumberOfCosts = parts.length !== ruleNames.length;
    const hasEmptyCost = parts.some((value) => value === "");
    const hasInvalidCost = costs.some(
      (value) => !Number.isFinite(value) || value < 0,
    );
  
    if (wrongNumberOfCosts || hasEmptyCost || hasInvalidCost) {
      window.alert(
        `Enter ${ruleNames.length} non-negative numbers in this order:\n` +
          ruleNames.join(", "),
      );
  
      return null;
    }
  
    return costs;
  }
  
  export function formatProblemGraphCosts(costs) {
    return Array.isArray(costs) ? costs.join(", ") : "";
  }