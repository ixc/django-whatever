from collections import defaultdict

NO_RETURNED_VALUE = type("NoReturnedValue", (), {})

def split_model_kwargs(kw):
    """
    Simple ORM query parser.
    """
    model_fields = {}
    fields_args = defaultdict(lambda : {})

    for key in kw.keys():
        if '__' in key:
            field, _, subfield = key.partition('__')
            fields_args[field][subfield] = kw[key]
        else:
            model_fields[key] = kw[key]

    return model_fields, fields_args


def valid_choices(choices):
    """
    Return the list of choices's keys.
    """
    for key, value in choices:
        if isinstance(value, (list, tuple)):
            for key, _ in value:
                yield key
        else:
            yield key

class Value(object):
    def __init__(self, value):
        self.value = value
