function queryParams(params) {
  const filter = params.filter ? JSON.parse(params.filter) : {};

  // Map frontend field names to API ordering fields
  const orderingMap = {
    'participant': 'participant__external_id',
    'blueprint': 'blueprint__name',
  };

  let sortField = params.sort;
  if (sortField && orderingMap[sortField]) {
    sortField = orderingMap[sortField];
  }

  return {
    limit: params.limit,
    offset: params.offset,
    ordering: params.order === 'desc' ? `-${sortField}` : sortField,
    ...filter
  };
}
