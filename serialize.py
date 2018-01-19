import pickle
import joblib
import sys
import os.path as path
from collections import defaultdict

DATA_DIR = "new_data/"
OBJ_DIR = "serialized_obj/"
sys.setrecursionlimit(20000)

def store_obj(obj, filename):
    file_path = path.join(OBJ_DIR, filename)
    print("Storing", file_path)
    joblib.dump(obj, file_path)
    # with open(file_path, "wb") as f:
    #     pickle.dump(obj, f)

def load_obj(filename):
    file_path = path.join(OBJ_DIR, filename)
    print("Loading", file_path)
    obj = joblib.load(file_path)
    # with open(file_path, "rb") as f:
    #     obj = pickle.load(f)
    return obj


def normal_mapping(sp, rt_dict):
    rt_dict[sp[0]] = sp[1]
def reverse_mapping(sp, rt_dict):
    rt_dict[sp[1]] = sp[0]
def aggregate_2side(sp, rt_dict1, rt_dict2):
    rt_dict1[sp[0]].append(sp[1])
    rt_dict2[sp[1]].append(sp[0])
def parse_value2(sp, rt_dict):
    rt_dict[sp[0]] = sp[1].split(";")

def file_op(name, file_in, mapping_func, rt_dict1, rt_dict2=None):
    print("Process", name)
    file_in_path = path.join(DATA_DIR, file_in)
    with open(file_in_path, "r", encoding = "utf-8") as f:
        for line in f.readlines():
            sp = line.split("\t")
            sp = [v.strip() for v in sp]
            if rt_dict2 != None:
                mapping_func(sp, rt_dict1, rt_dict2)
            else:
                mapping_func(sp, rt_dict1)
    print("Finish")

def serialize_data():
    print("Start serializing")
    cat_name_to_id = {}
    cat_id_to_title = {}
    cat_id_to_pages = {}
    page_id_to_title = {}
    cat_to_articles = defaultdict(list)
    article_to_cats = defaultdict(list)
    g = defaultdict(list)
    ginv = defaultdict(list)
    # all_id = set()
    # sub_id = set()

    # with open(path.join(DATA_DIR, "cat_full.txt"), "r", encoding = "utf-8") as f:
    #     for line in f.readlines():
    #         sp = line.split("\t")
    #         cat = sp[1].strip()
    #         cat_id = sp[0].strip()
    #         n_pages = sp[2].strip()
    #         cat_name_to_id[cat] = cat_id
    #         cat_id_to_title[cat_id] = cat
    #         cat_id_to_pages[cat_id] = int(n_pages)

    # file_op("g, ginv", "subcat_id_to_cat_id.txt", aggregate_2side, ginv, g)
    # file_op("cat_id_to_title", "page_cat.txt", normal_mapping, cat_id_to_title)
    # file_op("page_id_to_title", "page.txt", normal_mapping, page_id_to_title)
    # file_op("cat_to_articles", "agg_cat_id_to_article_id.txt", parse_value2, cat_to_articles)
    file_op("article_to_cats", "agg_article_id_to_cat_id.txt", parse_value2, article_to_cats)
    
    # root_id = all_id - sub_id
    # print(map(cat_id_to_title.get, root_id))
    # store_obj(cat_name_to_id, "cat_name_to_id.txt")
    # store_obj(cat_id_to_pages, "cat_id_to_pages.txt")
    
    # store_obj(g, "g.pkl")
    # store_obj(ginv, "ginv.pkl")
    # store_obj(cat_id_to_title, "cat_id_to_title.pkl")
    # store_obj(page_id_to_title, "page_id_to_title.pkl")
    # store_obj(cat_to_articles, "cat_to_articles.pkl")
    store_obj(article_to_cats, "article_to_cats.pkl")

    print("Finish serializing")

def precompute_page_data(g, id_to_pages):
    print("Start precomputing number of pages")
    id_to_num_pages = {}
    c = 0
    n = len(id_to_pages.keys())
    for node in id_to_pages.keys():
        c += 1
        print(c, "/", n)
        value = get_num_pages(g, id_to_pages, node)
        id_to_num_pages[node] = value
    store_obj(id_to_num_pages, "cat_id_to_total_pages.pkl")
    print("Finish")

def precompute_leaf_data(g, cat_id_to_title):
    print("Start precomputing number of leaf")
    id_to_num_leaves = {}
    c = 0
    n = len(cat_id_to_title.keys())
    for node in cat_id_to_title.keys():
        c += 1
        print(c, "/", n)
        value = get_num_leaves(g, node)
        id_to_num_leaves[node] = value
    store_obj(id_to_num_leaves, "cat_id_to_total_leaves.pkl")
    print("Finish")

def get_num_leaves(g, nid):
    visited = set()
    return get_num_leaves_support(g, nid, visited)

def get_num_leaves2(g, nids):
    visited = set()
    s = 0
    for nid in nids:
        s += get_num_leaves_support(g, nid, visited)
    return s

def get_num_leaves_support(g, nid, visited):
    visited.add(nid)
    # print (cat_id_to_title[nid],)
    if nid not in g:
        return 1
    s = 0
    for i in g[nid]:
        if i not in visited:
            s += get_num_leaves_support(g, i, visited)
    return s


def get_max_depth(g, nid):
    visited = set()
    # print("\n-----")
    return get_max_depth_support(g, nid, visited)

def get_max_depth_support(g, nid, visited):
    visited.add(nid)
    if nid not in g:
        return 1
    s = 0
    for i in g[nid]:
        if i not in visited:
            d = get_max_depth_support(g, i, visited)
            if d > s:
                s = d
    return s + 1

def get_num_children(g, nid):
    visited = set()
    # print("\n-----")
    return get_num_children_support(g, nid, visited)


def get_num_children_support(g, nid, visited):
    visited.add(nid)
    if nid not in g:
        return 1
    s = 0
    for i in g[nid]:
        if i not in visited:
            s += get_num_children_support(g, i, visited)
    return s + 1

def get_num_pages(g, cat_id_to_pages, nid):
    visited = set()
    return get_num_pages_support(g, cat_id_to_pages, nid, visited)

def get_num_pages_support(g, cat_id_to_pages, nid, visited):
    visited.add(nid)
    if nid not in g:
        return cat_id_to_pages[nid]
    s = 0
    for i in g[nid]:
        if i not in visited:
            s += get_num_pages_support(g, cat_id_to_pages, i, visited)
    return s + cat_id_to_pages[nid]

# serialize_data()
# exit()

g = load_obj("g.pkl")
cat_id_to_title = load_obj("cat_id_to_title.pkl")
precompute_leaf_data(g, cat_id_to_title)