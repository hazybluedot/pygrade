def maybe(this, name, orthat):
    try:
        return this[name]
    except KeyError as e:
        return orthat
