export type EntryGroup = { groupId: number, rows: Record<string, any>[] };

type ExtractionOutcome = {
  extractedData: Record<string, any>[];
  rowGroupIds: number[];
};

/**
 * Groups extractedData rows by the hidden rowGroupIds stamped during
 * extraction (see BlueprintExtractionOutcome.nextGroupId), preserving the
 * order groups were first encountered.
 */
export function groupEntriesByRowGroupId(outcome: ExtractionOutcome): EntryGroup[] {
  const order: number[] = [];
  const byGroupId = new Map<number, Record<string, any>[]>();

  outcome.extractedData.forEach((row, i) => {
    const groupId = outcome.rowGroupIds[i];
    if (!byGroupId.has(groupId)) {
      byGroupId.set(groupId, []);
      order.push(groupId);
    }
    byGroupId.get(groupId)!.push(row);
  });

  return order.map(groupId => ({ groupId, rows: byGroupId.get(groupId)! }));
}
