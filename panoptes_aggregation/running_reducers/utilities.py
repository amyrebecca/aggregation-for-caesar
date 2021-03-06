'''Unility used for transforming a list of extracted data for use in tests'''
import copy


def extract_in_data(extracted_data, store={}, **kwargs_extra_data):
    extracted_request_data = {
        'extracts': [],
        'store': store
    }
    for ddx, data in enumerate(extracted_data):
        output_extract = {'data': copy.deepcopy(data)}
        for key in kwargs_extra_data.keys():
            output_extract[key] = kwargs_extra_data[key][ddx]
        extracted_request_data['extracts'].append(output_extract)
    return extracted_request_data
