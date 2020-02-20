def union(include, default):
    return include + list(set(default) - set(include))
