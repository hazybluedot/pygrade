import collections

def find_key(searchkey, struct):
    if hasattr(struct, 'keys'):
        #sys.stderr.write("Searching for {0} in {1}\n".format(searchkey, struct.keys()))
        if searchkey in struct.keys():
            return struct[searchkey]
        else:
            for (key, value) in struct.items():
                result = find_key(searchkey, value)
                if result:
                    return result
    elif isinstance(struct, collections.Iterable) and not isinstance(struct, str):
        #sys.stderr.write("iterating over {0}\n".format(struct))
        if len(struct) > 1:
            for item in struct:
                result = find_key(searchkey, item)
                if result:
                    return result
    return None
