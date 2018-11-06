import json
import functools

class pipe(object):
    def __init__(self, function):
        self.function = function
        functools.update_wrapper(self, function)

    def __rrshift__(self, other):
        return self.function(other)

    def __call__(self, *args, **kwargs):
        return pipe(lambda x: self.function(x, *args, **kwargs))


@pipe
def to_dic(string_or_binary):
    return json.loads(string_or_binary)



@pipe
def dump_dic(dic: dict, filename: str):
    with open(filename, "w") as f:
        json.dump(dic, f)


@pipe
def load_file_to_dic(filename: str):
    with open(filename, 'r') as f:
        return json.load(f)