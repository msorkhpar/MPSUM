import csv


# eid	dataset	class	euri	elabel	tripleNum
def read_source_csv_file(path):
    with open(path, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter='	', quotechar='|')
        result = list(csv_reader)
        return result


def read_nt_file(data_root, dataset, eid):
    path = '{0}/{1}/{2}/{2}_rank.nt'.format(data_root, dataset, eid)
    with open(path) as opened_file:
        csv_reader = csv.reader(opened_file, delimiter=' ', quotechar='|')
        result = list(csv_reader)
        return result


def find_top(file, search_key, data_root, dataset, eid):
    formatted_key = '<{0}>'.format(search_key)
    result = []
    for line in file:
        if (line[0] == formatted_key) | (line[-2] == formatted_key):
            result.append(line)      
            if (len(result) == 5) | (len(result) == 10):
                write_top('{0}/{1}/{2}/{2}_top{3}.nt'.format(data_root, dataset, eid, len(result)), result)
            if len(result) == 10:
                return


def write_top(file, file_contents):
    with open(file, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in file_contents:
            spamwriter.writerow(row)


for key in read_source_csv_file("elist.txt")[1:]:
    # dataset 1
    nt_file = read_nt_file("result_1", key[1], key[0])
    find_top(nt_file, key[3], "result_1", key[1], key[0])
    # dataset 2
    nt_file = read_nt_file("results_kafca", key[1], key[0])
    find_top(nt_file, key[3], "results_kafca", key[1], key[0])
