from hashlib import md5
import json

def escape(key):
    key = key.replace('\\', r'\\')
    return key.replace('.', r'\.')

def generate_hashes_with_strings(nest_value, nest_key='', order=0):
    # Are we now looking at a list or a dict?
    if isinstance(nest_value, dict):
        iter_tuple = nest_value.items()
        in_list = False
    else:
        iter_tuple = enumerate(nest_value)
        in_list = True

    # Loop through each element and re-call this function
    # if it's a list or a dict.
    for key, value in iter_tuple:
        if not in_list:
            escaped_key = escape(key)
        else:
            escaped_key = u'..{}..'.format(key)

        if isinstance(value, dict):
            new_nest = '{}{}{}'.format(nest_key, escaped_key, '.')
            for key, value in generate_hashes_with_strings(value, new_nest, order):
                yield key, value
        elif isinstance(value, list):
            new_nest = '{}{}'.format(nest_key, escaped_key)
            for key, value in generate_hashes_with_strings(value, new_nest, order):
                yield key, value
        else:
            entity_key = u'{}{}'.format(nest_key, escaped_key)

            keys = [entity_key, '']
            # hashed_keys = md5(':'.join(keys).encode('utf-8')).hexdigest()
            hashed_keys = ':'.join(keys).encode('utf-8')
            yield hashed_keys, value

        order += 1
