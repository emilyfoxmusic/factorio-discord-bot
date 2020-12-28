def single(fn, iter):
  filtered = list(filter(fn, iter))
  if len(filtered) == 0:
    raise Exception('Item not found')
  if len(filtered) > 1:
    raise Exception('More than one item found')
  return filtered[0]