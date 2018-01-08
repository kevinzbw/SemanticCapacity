import pickle
import matplotlib.pyplot as plt
import numpy as np
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from collections import defaultdict

def store_obj(obj, filename):
    with open(filename, "wb") as f:
        pickle.dump(obj, f)

def load_obj(filename):
    with open(filename, "rb") as f:
        obj = pickle.load(f)
    return obj

def generate_data():
    print("started to serialize")
    name_to_id = defaultdict(int)
    id_to_name = defaultdict(int)
    id_to_pages = defaultdict(int)
    g = defaultdict(list)
    ginv = defaultdict(list)
    # all_id = set()
    # sub_id = set()
    with open("data/subcat_cat_id.txt", "r", encoding = "ISO-8859-1") as f:
        for line in f.readlines():
            sp = line.split("\t")
            subcat = sp[0].strip()
            cat = sp[1].strip()
            g[cat].append(subcat)
            ginv[subcat].append(cat)
            
    with open("data/official_cat.txt", "r", encoding = "ISO-8859-1") as f:
        for line in f.readlines():
            sp = line.split("\t")
            cat = sp[1].strip()
            cat_id = sp[0].strip()
            n_pages = sp[2].strip()
            name_to_id[cat] = cat_id
            id_to_name[cat_id] = cat
            id_to_pages[cat_id] = int(n_pages)
    # root_id = all_id - sub_id
    # print(map(id_to_name.get, root_id))
    store_obj(name_to_id, "name_to_id.txt")
    store_obj(id_to_name, "id_to_name.txt")
    store_obj(id_to_pages, "id_to_pages.txt")
    store_obj(g, "g.txt")
    store_obj(ginv, "ginv.txt")
    print("finished")

def precompute_data(g, id_to_pages):
    id_to_num_pages = {}
    c = 0
    n = len(id_to_pages.keys())
    for node in id_to_pages.keys():
        c += 1
        print(c, "/", n)
        value = get_num_pages(g, id_to_pages, node)
        id_to_num_pages[node] = value
    store_obj(id_to_num_pages, "id_to_total_pages.txt")
    print("finished")

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
    # print (id_to_name[nid],)
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

def get_num_pages(g, id_to_pages, nid):
    visited = set()
    return get_num_pages_support(g, id_to_pages, nid, visited)

def get_num_pages_support(g, id_to_pages, nid, visited):
    visited.add(nid)
    if nid not in g:
        return id_to_pages[nid]
    s = 0
    for i in g[nid]:
        if i not in visited:
            s += get_num_pages_support(g, id_to_pages, i, visited)
    return s + id_to_pages[nid]

def get_category_weight(g, cat_id):
    return get_num_leaves(g, cat_id)

def get_categories_avg_weight(g, cat_ids):
    return get_num_leaves2(g, cat_ids)

def get_category_norm_weight(g, g_inv, cat_id):
    parent_cats = g_inv[cat_id]
    parent_values = [get_num_leaves(g, p_cat_id) for p_cat_id in parent_cats]
    value = get_num_leaves(g, cat_id)
    s = sum(parent_values)
    if s:
        return value/s
    else:
        return s

def get_category_pages_weight(g, g_inv, id_to_pages, cat_id):
    return get_num_pages(g, id_to_pages, cat_id)

def get_category_pages_norm_weight(g, g_inv, id_to_pages, cat_id):
    parent_cats = g_inv[cat_id]
    parent_values = [get_num_pages(g, id_to_pages, p_cat_id) for p_cat_id in parent_cats]
    value = get_num_pages(g, id_to_pages, cat_id)
    s = sum(parent_values)
    if s:
        return value/s
    else:
        return s

def get_article_weight(search, g, title):
    results = search_article_title(search, title)
    # print(results)
    s = 0
    s_score = 0
    for r in results:
        score, title, cat_list = r
        s_score += score
        cat_weights = [get_category_weight(g, cat_id) for cat_id in cat_list]
        print(cat_weights)
        article_weight = score*sum(cat_weights)/len(cat_weights)
        s += article_weight
    if s:
        s = s/len(results)/s_score
    return s

def get_article_avg_weight(search, g, title):
    results = search_article_title(search, title)
    # print(results)
    s = []
    s_score = 0
    for r in results:
        score, title, cat_list = r
        s_score += score
        cat_weight = get_categories_avg_weight(g, cat_list)
        print(cat_weight)
        article_weight = score*cat_weight
        s.append(article_weight)
    top_weights = sorted(s, reverse=True)[0:3]
    return sum(top_weights)/len(top_weights)/s_score

def get_article_pre_weight(search, id_to_weight, title):
    results = search_article_title(search, title)
    # print(results)
    s = 0
    s_score = 0
    for r in results:
        score, title, cat_list = r
        s_score += score
        cat_weights = [id_to_weight[cat_id] for cat_id in cat_list]
        print(cat_weights)
        article_weight = score*sum(cat_weights)/len(cat_weights)
        s += article_weight
    if s:
        s = s/len(results)/s_score
    return s

def get_article_norm_weight(search, g, ginv, title):
    results = search_article_title(search, title)
    # print(results)
    s = 0
    s_score = 0
    for r in results:
        score, title, cat_list = r
        s_score += score
        cat_weights = [get_category_norm_weight(g, ginv, cat_id) for cat_id in cat_list]
        print(cat_weights)
        article_weight = score*sum(cat_weights)/len(cat_weights)
        s += article_weight
    if s:
        s = s/len(results)/s_score
    return s

def get_article_pages_weight(search, g, ginv, id_to_pages, title):
    results = search_article_title(search, title)
    # print(results)
    s = 0
    s_score = 0
    for r in results:
        score, title, cat_list = r
        s_score += score
        cat_weights = [get_category_pages_weight(g, ginv, id_to_pages, cat_id) for cat_id in cat_list]
        print(cat_weights)
        article_weight = score*sum(cat_weights)/len(cat_weights)
        s += article_weight
    if s:
        s = s/len(results)/s_score
    return s

def get_article_pages_norm_weight(search, g, ginv, id_to_pages, title):
    results = search_article_title(search, title)
    # print(results)
    s = 0
    s_score = 0
    for r in results:
        score, title, cat_list = r
        s_score += score
        cat_weights = [get_category_pages_norm_weight(g, ginv, id_to_pages, cat_id) for cat_id in cat_list]
        print(cat_weights)
        article_weight = score*sum(cat_weights)/len(cat_weights)
        s += article_weight
    if s:
        s = s/len(results)/s_score
    return s

def search_article_title(search, title):
    s = search.query("match", title=title)[0:10]
    response = s.execute()
    rt = []
    for h in response:
        rt.append([h.meta.score, h.title, h.category_list])
        print(h.meta.score, h.title, h.category_list)
    return rt

def plot(terms, weights):
    plt.figure()
    pos = list(range(len(terms)))
    width = 0.25 
    plt.bar(pos, weights, align='center', alpha=0.5)
    plt.xticks(pos, terms)
    plt.ylabel('Capacity')
    plt.title('Capacity of Terms')
    plt.show()

# generate_data()
# id_to_name = load_obj("id_to_name.txt")
# name_to_id = load_obj("name_to_id.txt")
id_to_pages = load_obj("id_to_pages.txt")
g = load_obj("g.txt")
ginv = load_obj("ginv.txt")
precompute_data(g, id_to_pages)
id_to_num_pages = load_obj("id_to_num_pages.txt")






