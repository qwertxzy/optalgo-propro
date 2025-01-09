def flatten(xss):
  '''Flatten nested list'''
  return [x for xs in xss for x in xs]
