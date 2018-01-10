import pickle
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from collections import defaultdict
import fuzzywuzzy as fuzz

def store_obj(obj, filename):
    with open(filename, "wb") as f:
        pickle.dump(obj, f)

def load_obj(filename):
    with open(filename, "rb") as f:
        obj = pickle.load(f)
    return obj

def generate_data():
    print("started to serialize")
    cat_name_to_id = defaultdict(int)
    cat_id_to_name = defaultdict(int)
    cat_id_to_pages = defaultdict(int)
    article_id_to_name = defaultdict(int)
    cat_to_articles = defaultdict(list)
    article_to_cats = defaultdict(list)
    g = defaultdict(list)
    ginv = defaultdict(list)
    # all_id = set()
    # sub_id = set()
    with open("data/subcat_id_to_cat_id.txt", "r", encoding = "utf-8") as f:
        for line in f.readlines():
            sp = line.split("\t")
            subcat = sp[0].strip()
            cat = sp[1].strip()
            g[cat].append(subcat)
            ginv[subcat].append(cat)
            
    with open("data/cat_full.txt", "r", encoding = "utf-8") as f:
        for line in f.readlines():
            sp = line.split("\t")
            cat = sp[1].strip()
            cat_id = sp[0].strip()
            n_pages = sp[2].strip()
            cat_name_to_id[cat] = cat_id
            cat_id_to_name[cat_id] = cat
            cat_id_to_pages[cat_id] = int(n_pages)

    with open("data/article_id_to_article_title.txt", "r", encoding = "utf-8") as f:
        for line in f.readlines():
            sp = line.split("\t")
            article_id = sp[0].strip()
            article_title = sp[1].strip()
            article_id_to_name[article_id] = article_title
    
    with open("data/agg_cat_id_to_article_id.txt", "r", encoding = "utf-8") as f:
        for line in f.readlines():
            sp = line.split("\t")
            cat_id = sp[0].strip()
            articles_id = sp[1].strip().split(";")
            cat_to_articles[cat_id] = articles_id
            
    with open("data/agg_article_id_to_cat_id.txt", "r", encoding = "utf-8") as f:
        for line in f.readlines():
            sp = line.split("\t")
            article_id = sp[0].strip()
            cats_id = sp[1].strip().split(";")
            article_to_cats[article_id] = cats_id
    
    # root_id = all_id - sub_id
    # print(map(cat_id_to_name.get, root_id))
    store_obj(cat_name_to_id, "cat_name_to_id.txt")
    store_obj(cat_id_to_name, "cat_id_to_name.txt")
    store_obj(cat_id_to_pages, "cat_id_to_pages.txt")
    store_obj(article_id_to_name, "article_id_to_name.txt")
    store_obj(article_to_cats, "article_to_cats.txt")
    store_obj(cat_to_articles, "cat_to_articles.txt")
    store_obj(g, "g.txt")
    store_obj(ginv, "ginv.txt")
    print("finished")

def precompute_page_data(g, id_to_pages):
    id_to_num_pages = {}
    c = 0
    n = len(id_to_pages.keys())
    for node in id_to_pages.keys():
        c += 1
        print(c, "/", n)
        value = get_num_pages(g, id_to_pages, node)
        id_to_num_pages[node] = value
    store_obj(id_to_num_pages, "cat_id_to_total_pages2.txt")
    print("finished")

def precompute_leaf_data(g, cat_id_to_name):
    id_to_num_leaves = {}
    c = 0
    n = len(cat_id_to_name.keys())
    for node in cat_id_to_name.keys():
        c += 1
        print(c, "/", n)
        if node in g:
            value = get_num_leaves(g, node)
            id_to_num_leaves[node] = value
        else:
            id_to_num_leaves[node] = 1
    store_obj(id_to_num_leaves, "cat_id_to_total_leaves2.txt")
    print("finished")

def get_num_leaves(g, nid):
    visited = set()
    return get_num_leaves_support(g, nid, visited)

def get_num_leaves_support(g, nid, visited):
    visited.add(nid)
    # print (cat_id_to_name[nid],)
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


g = load_obj("g.txt")
cat_id_to_name = load_obj("cat_id_to_name.txt")
precompute_leaf_data(g, cat_id_to_name)