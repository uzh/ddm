import { DateTime } from "luxon";

function getOriginalValueAsString(v) {
  if (typeof v !== 'string') {
    return JSON.stringify(v);
  } else {
    return v;
  }
}

function isNumeric(v){
  if (typeof v === 'number') return true;
  if (typeof v != 'string') return false;
  return !isNaN(v) && !isNaN(parseFloat(v));
}

function bothDates(entryValue, comparisonValue) {
  try {
      if (DateTime.fromISO(entryValue).isValid && DateTime.fromISO(comparisonValue).isValid ) {
    // e.g., "2016-05-25T092415.123", "2016-05-25"
    return true;

    } else if (DateTime.fromRFC2822(entryValue).isValid && DateTime.fromRFC2822(comparisonValue).isValid ) {
      // e.g., "Tue, 01 Nov 2016 13:23:12 +0630"
      return true;

    } else if (DateTime.fromHTTP(entryValue).isValid && DateTime.fromHTTP(comparisonValue).isValid ) {
      // e.g., "Sunday, 06-Nov-94 08:49:37 GMT"
      return true;

    } else {
      return false;
    }
  }
  catch(err) {
    return false;
  }
}

function getDates(entryValue, comparisonValue) {
  if (DateTime.fromISO(entryValue).isValid && DateTime.fromISO(comparisonValue).isValid) {
    return [DateTime.fromISO(entryValue), DateTime.fromISO(comparisonValue)];

  } else if (DateTime.fromRFC2822(entryValue).isValid && DateTime.fromRFC2822(comparisonValue).isValid) {
    return [DateTime.fromRFC2822(entryValue), DateTime.fromRFC2822(comparisonValue)];

  } else if (DateTime.fromHTTP(entryValue).isValid && DateTime.fromHTTP(comparisonValue).isValid) {
    return [DateTime.fromHTTP(entryValue), DateTime.fromHTTP(comparisonValue)];

  } else {
    return [null, null]
  }
}

function prepareValues(entryValue, comparisonValue) {
  if (isNumeric(entryValue) && isNumeric(comparisonValue)) {
    entryValue = parseFloat(entryValue);
    comparisonValue = parseFloat(comparisonValue);
  } else if (bothDates(entryValue, comparisonValue)) {
    [entryValue, comparisonValue] = getDates(entryValue, comparisonValue)
  } else {
    entryValue = getOriginalValueAsString(entryValue);
    comparisonValue = getOriginalValueAsString(comparisonValue);
  }
  return [entryValue, comparisonValue];
}

export function valueIsEqual(entryValue, comparisonValue) {
  entryValue = getOriginalValueAsString(entryValue);
  comparisonValue = getOriginalValueAsString(comparisonValue);
  return entryValue === comparisonValue;
}

export function valueIsNotEqual(entryValue, comparisonValue) {
  entryValue = getOriginalValueAsString(entryValue);
  comparisonValue = getOriginalValueAsString(comparisonValue);
  return entryValue !== comparisonValue;
}

export function valueIsSmallerOrEqual(entryValue, comparisonValue) {
  if (bothDates(entryValue, comparisonValue) ||
    (isNumeric(entryValue) && isNumeric(comparisonValue))) {
    [entryValue, comparisonValue] = prepareValues(entryValue, comparisonValue);
    return entryValue <= comparisonValue;
  } else {
    return false;
  }
}

export function valueIsGreaterOrEqual(entryValue, comparisonValue) {
  if (bothDates(entryValue, comparisonValue) ||
    (isNumeric(entryValue) && isNumeric(comparisonValue))) {
    [entryValue, comparisonValue] = prepareValues(entryValue, comparisonValue);
    return entryValue >= comparisonValue;
  } else {
    return false;
  }
}

export function valueIsSmaller(entryValue, comparisonValue) {
  if (bothDates(entryValue, comparisonValue) ||
    (isNumeric(entryValue) && isNumeric(comparisonValue))) {
    [entryValue, comparisonValue] = prepareValues(entryValue, comparisonValue);
    return entryValue < comparisonValue;
  } else {
    return false;
  }
}

export function valueIsGreater(entryValue, comparisonValue) {
  if (bothDates(entryValue, comparisonValue) ||
    (isNumeric(entryValue) && isNumeric(comparisonValue))) {
    [entryValue, comparisonValue] = prepareValues(entryValue, comparisonValue);
    return entryValue > comparisonValue;
  } else {
    return false;
  }
}

export function regexDeleteMatch(entryValue, comparisonValue) {
  let originalValue = getOriginalValueAsString(entryValue);
  let comparisonRegExp = RegExp(comparisonValue, 'g');
  return originalValue.replaceAll(comparisonRegExp, '');
}

export function regexReplaceMatch(entryValue, comparisonValue, replacementValue) {
  let originalValue = getOriginalValueAsString(entryValue);
  let comparisonRegExp = RegExp(comparisonValue, 'g');
  return originalValue.replaceAll(comparisonRegExp, replacementValue);
}

export function regexDeleteRow(entryValue, comparisonValue) {
  let originalValue = getOriginalValueAsString(entryValue);
  let comparisonRegExp = RegExp(comparisonValue, 'g');
  return comparisonRegExp.test(originalValue);
}
