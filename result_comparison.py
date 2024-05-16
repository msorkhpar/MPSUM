import os
import re
import json

from rdflib.graph import Graph

grd_root = 'E:\\dev\\src\\github.com\\nju-websoft\\ESBM\\v1.2\\ESBM_benchmark_v1.2'
top_num_regex = '(\d+)_top(\d+).nt'
ground_match_regex = '{0}_gold_top{1}_\d+.nt'
results = dict()
x = {
    'result_1': {
        'dbpedia_5': .3,
        'dbpedia_10': .672,
        'lmdb_5': 1,
        'lmdb_10': .555,
    }
}


def load_nt_file(path):
    label = Graph()
    triples_labels = []
    label = label.parse(path, format='nt')

    for s, p, o in label:
        triples_labels.append([s.n3(), p.n3(), o.n3()])

    return triples_labels


def eval_average_precision(ground_truth_summary, predicted_summary):
    # Calculate average precision
    relevant_count = 0
    cumulative_precision = 0

    # Iterate over each predicted summary
    for i, summary in enumerate(predicted_summary):
        if summary in ground_truth_summary:
            relevant_count += 1
            precision_at_i = relevant_count / (i + 1)
            cumulative_precision += precision_at_i

    # Calculate average precision for this entity
    if relevant_count > 0:
        average_precision = cumulative_precision / len(ground_truth_summary)
        average_precision = average_precision
    else:
        average_precision = 0

    return average_precision


def read_result_folder(folder, run_name):
    results[run_name] = {
        'dbpedia_5': 0,
        'dbpedia_5_total': 0,
        'dbpedia_5_count': 0,
        'dbpedia_10': 0,
        'dbpedia_10_total': 0,
        'dbpedia_10_count': 0,
        'lmdb_5': 0,
        'lmdb_5_total': 0,
        'lmdb_5_count': 0,
        'lmdb_10': 0,
        'lmdb_10_total': 0,
        'lmdb_10_count': 0,
    }
    for (root, dirs, files) in os.walk(folder + os.sep + run_name, topdown=True):
        if len(files) > 0:
            folders = root.split(os.sep)
            node = folders[-1]
            db = folders[-2]
            ground_folder, ground_files = fetch_ground_truth(node, db)
            for file in files:
                match = re.search(top_num_regex, file)
                if match:
                    entry_id = match.group(1)
                    top_count = match.group(2)
                    predicted = load_nt_file(root + os.sep + file)
                    for gf in ground_files:
                        if re.match(ground_match_regex.format(entry_id, top_count), gf):
                            ground_truth = load_nt_file(ground_folder + os.sep + gf)
                            average_precision = eval_average_precision(ground_truth, predicted)
                            print(average_precision)
                            results[run_name]['{0}_{1}_total'.format(db, top_count)] += average_precision
                            results[run_name]['{0}_{1}_count'.format(db, top_count)] += 1
    results[run_name]['dbpedia_5'] = results[run_name]['dbpedia_5_total'] / results[run_name]['dbpedia_5_count']
    results[run_name]['dbpedia_10'] = results[run_name]['dbpedia_10_total'] / results[run_name]['dbpedia_10_count']
    results[run_name]['lmdb_5'] = results[run_name]['lmdb_5_total'] / results[run_name]['lmdb_5_count']
    results[run_name]['lmdb_10'] = results[run_name]['lmdb_10_total'] / results[run_name]['lmdb_10_count']


# Directory path: E:\dev\src\github.com\msorkhpar\MPSUM/result_9\lmdb\168
# Files Names: ['168_rank.nt', '168_top10.nt', '168_top5.nt']
# Ground Truth: v1.2/ESBM_benchmark_v1.2/lmdb_data/168/168_gold_top5_0.nt
def fetch_ground_truth(node, db):
    path = '{0}{3}{1}_data{3}{2}'.format(grd_root, db, node, os.sep)
    for (root, dirs, files) in os.walk(path, topdown=True):
        if len(dirs) > 0:
            raise ValueError('fetch_ground_truth: directory found')
        return path, files
    raise ValueError('fetch_ground_truth: should not reach here')


def loop_results():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    for result_run in range(1, 10):
        run_name = "result_" + str(result_run)
        read_result_folder(dir_path, run_name)
    pretty = json.dumps(results, indent=4)
    print(pretty)
    with open(dir_path + os.sep + 'result_comparison_results.json', 'w') as file_name:
        file_name.write(pretty)
        file_name.close()


loop_results()
