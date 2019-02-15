from functools import wraps
from ..reducers.process_kwargs import process_kwargs
from ..append_version import append_version, remove_version


def running_reducer_wrapper(
    process_data=None,
    defaults_process=None,
    defaults_data=None,
    relevant_reduction=False
):
    def decorator(func):
        @wraps(func)
        def wrapper(argument, **kwargs):
            kwargs_process = {}
            kwargs_data = {}
            kwargs_extra_data = {}
            #: check if argument is a flask request
            if hasattr(argument, 'get_json'):
                kwargs = argument.args.copy().to_dict()
                data_in = argument.get_json()['data']
                store = argument.get_json()['store']
                remove_version(data_in)
                if relevant_reduction:
                    kwargs_extra_data['relevant_reduction'] = argument.get_json()['relevant_reduction']
            else:
                data_in = argument
                store = kwargs['store']
                remove_version(data_in)
                if relevant_reduction:
                    kwargs_extra_data['relevant_reduction'] = kwargs['relevant_reduction']
            no_version = kwargs.pop('no_version', False)
            if defaults_process is not None:
                kwargs_process = process_kwargs(kwargs, defaults_process)
            if defaults_data is not None:
                kwargs_data = process_kwargs(kwargs, defaults_data)
            if process_data is not None:
                data = process_data(data_in, **kwargs_process)
            else:
                data = data_in
            reduction = func(data, store=store, **kwargs_data, **kwargs_extra_data)
            if not no_version:
                append_version(reduction)
            return reduction
        #: keep the orignal function around for testing
        #: and access by other reducers
        wrapper._original = func
        return wrapper
    return decorator
