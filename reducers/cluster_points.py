import numpy as np
from sklearn.cluster import DBSCAN
from .process_kwargs import process_kwargs
from flask import jsonify, request


DEFAULTS = {
    'eps': {'default': 5.0, 'type': float},
    'min_samples': {'default': 3, 'type': int},
    'metric': {'default': 'euclidean', 'type': str},
    'algorithm': {'default': 'auto', 'type': str},
    'leaf_size': {'default': 30, 'type': int},
    'p': {'default': None, 'type': float}
}


def process_data(data):
    unique_tools = set(sum([['_'.join(k.split('_')[:-1]) for k in d.keys()] for d in data], []))
    data_by_tool = {}
    for tool in unique_tools:
        for d in data:
            data_by_tool.setdefault(tool, [])
            if ('{0}_x'.format(tool) in d) and ('{0}_y'.format(tool) in d):
                data_by_tool[tool] += list(zip(d['{0}_x'.format(tool)], d['{0}_y'.format(tool)]))
    return data_by_tool


def cluster_points(data_by_tool, **kwargs):
    clusters = {}
    for tool, loc_list in data_by_tool.items():
        loc = np.array(loc_list)
        if loc.shape[0] > kwargs['min_samples']:
            db = DBSCAN(**kwargs).fit(np.array(loc))
            clusters['{0}_cluster_labels'.format(tool)] = db.labels_
            for k in set(db.labels_):
                if k > -1:
                    idx = db.labels_ == k
                    # number of points in the cluster
                    clusters.setdefault('{0}_clusters_count'.format(tool), []).append(int(idx.sum()))
                    # mean of the cluster
                    k_loc = loc[idx].mean(axis=0)
                    clusters.setdefault('{0}_clusters_x'.format(tool), []).append(float(k_loc[0]))
                    clusters.setdefault('{0}_clusters_y'.format(tool), []).append(float(k_loc[1]))
                    # cov matrix of the cluster
                    k_cov = np.cov(loc[idx].T)
                    clusters.setdefault('{0}_clusters_var_x'.format(tool), []).append(float(k_cov[0, 0]))
                    clusters.setdefault('{0}_clusters_var_y'.format(tool), []).append(float(k_cov[1, 1]))
                    clusters.setdefault('{0}_clusters_var_x_y'.format(tool), []).append(float(k_cov[0, 1]))
    return clusters


def reducer_request(request):
    data = process_data([d['data'] for d in request.get_json()])
    kwargs = process_kwargs(request.args, DEFAULTS)
    return cluster_points(data, **kwargs)
