export function evaluateFilter(valueLeft, valueRight, operator) {
    switch (operator) {
        case '==':
            return valueLeft == valueRight;
        case '!=':
            return valueLeft != valueRight;
        case '>':
            return valueLeft > valueRight;
        case '<':
            return valueLeft < valueRight;
        case '>=':
            return valueLeft >= valueRight;
        case '<=':
            return valueLeft <= valueRight;
        case 'contains':
            return String(value_left).includes(String(value_right));
        case 'contains_not':
            return !String(value_left).includes(String(value_right));
        default:
            throw new Error(`Invalid operator: ${operator}`);
    }
}

export function evaluateFilterChain(arr) {
    // Step 1: Resolve all AND operations first
    let intermediate = [];
    let i = 0;

    while (i < arr.length) {
        if (arr[i] === 'AND') {
            let prev = intermediate.pop(); // Take last value
            let next = arr[i + 1]; // Take next value
            intermediate.push(prev && next); // Evaluate AND
            i += 2; // Skip the next value since it's already used
        } else {
            intermediate.push(arr[i]);
            i++;
        }
    }

    // Step 2: Resolve OR operations
    return intermediate.reduce((acc, curr) => acc || curr);
}
