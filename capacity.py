import pickle
import matplotlib.pyplot as plt
import numpy as np
import os.path as path
from copy import deepcopy
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from collections import defaultdict
from fuzzywuzzy import fuzz

DATA_DIR = "new_data/"
OBJ_DIR = "serialized_obj/"

def store_obj(obj, filename):
    file_path = path.join(OBJ_DIR, filename)
    print("Storing", file_path)
    with open(file_path, "wb") as f:
        pickle.dump(obj, f)

def load_obj(filename):
    file_path = path.join(OBJ_DIR, filename)
    print("Loading", file_path)
    with open(file_path, "rb") as f:
        obj = pickle.load(f)
    return obj

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

def get_category_pages_weight(g, g_inv, cat_id_to_pages, cat_id):
    return get_num_pages(g, cat_id_to_pages, cat_id)

def get_category_pages_norm_weight(g, g_inv, cat_id_to_pages, cat_id):
    parent_cats = g_inv[cat_id]
    parent_values = [get_num_pages(g, cat_id_to_pages, p_cat_id) for p_cat_id in parent_cats]
    value = get_num_pages(g, cat_id_to_pages, cat_id)
    s = sum(parent_values)
    if s:
        return value/s
    else:
        return s

def get_category_pre_pages_norm_weight(g, g_inv, id_to_total_pages, cat_id):
    parent_cats = g_inv[cat_id]
    parent_values = [id_to_total_pages[p_cat_id] for p_cat_id in parent_cats]
    value = id_to_total_pages[cat_id]
    s = sum(parent_values)
    if s:
        return value/s
    else:
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

def get_article_weight_gen(search, title, weight_method, argv):
    results = search_article_title(search, title)
    # results = reselect_candidate(results)
    # for _, name, _ in results:
    #     print("Candidate:", name)
    s = 0
    s_score = 0
    for r in results:
        score, article_id, title, cat_list = r
        s_score += score
        if isinstance(weight_method, dict):
            cat_weights = [weight_method[cat_id] for cat_id in cat_list]
        else:
            cat_weights = [weight_method(*argv, cat_id) for cat_id in cat_list]
        print(cat_weights)
        article_weight = score*sum(cat_weights)/len(cat_weights)
        # article_weight = score*sum(cat_weights)
        s += article_weight
    if s:
        s = s/len(results)/s_score
    return s

def search_article_title(search, title):
    s = search.query("match", article_title=title)[0:5]
    response = s.execute()
    rt = []
    for h in response:
        rt.append([h.meta.score, h.id, h.article_title, h.category_list])
        print(h.meta.score, h.id, h.article_title, h.category_list)
    return rt

def DFS_support(cat_id, g, depth, visited):
    if cat_id in visited:
        return
    if depth == 0:
        return
    visited.add(cat_id)
    for cat in g[cat_id]:
        if cat not in visited:
            DFS_support(cat, g, depth-1, visited)

def DFS(cats, g, depth):
    visited = set()
    for cat in cats:
        DFS_support(cat, g, depth, visited)
    return visited

def mark_component(i, c, connected, marked):
    marked[i] = c
    for j in range(i+1, len(connected)):
        if connected[i, j] == 1:
            mark_component(j, c, connected, marked)

def get_component_index(candidates):
    global g, ginv, id_to_total_pages, id_to_total_leaves
    n = len(candidates)
    connected = np.zeros((n, n))
    reachable = []
    for i in range(n):
        reachable.append(DFS(candidates[i], g, 3) | DFS(candidates[i], ginv, 3) )
    for i in range(n-1):
        for j in range(i+1, n):
            connected[i, j] = 1 if len(reachable[i] & reachable[j]) != 0 else 0
    marked = {}
    c = 0
    # for cp in connected:
    #     print(cp)
    for i in range(n):
        if i not in marked:
            mark_component(i, c, connected, marked)
            c += 1
    component = defaultdict(list)
    component_weight = defaultdict(int)
    for key, value in marked.items():
        component[value].append(key)
    for cp, index_candidates in component.items():
        for index in index_candidates:
            new_weight = np.sum([id_to_total_leaves[cat] for cat in candidates[index]]) / len(candidates[index])
            component_weight[cp] += new_weight
        component_weight[cp] /= len(index_candidates)
    best_component = None
    best_v = 0
    print(component)
    print(component_weight)
    for cp, value in component_weight.items():
        if best_v < value:
            best_v = value
            best_component = cp
    # best_candidate = None
    # best_v = 0
    # for i in component[best_component]:
    #     value = np.sum([id_to_total_leaves[cat] for cat in candidates[i]]) / len(candidates[i])
    #     if best_v < value:
    #         best_v = value
    #         best_candidate = i
    return component[best_component]

def reselect_candidate(results):
    candidates = [set(results[i][2]) for i in range(len(results))]
    # t = deepcopy(candidates[-1])
    # candidates[-1] = deepcopy(candidates[0])
    # candidates[0] = t
    major_component = get_component_index(candidates)
    new_results = [results[i] for i in major_component]
    print(major_component)
    return new_results    

def plot(terms, weights):
    plt.figure()
    pos = list(range(len(terms)))
    width = 0.25 
    plt.bar(pos, weights, align='center', alpha=0.5)
    plt.xticks(pos, terms)
    plt.ylabel('Capacity')
    plt.title('Capacity of Terms')
    plt.show()

def test(term, weight_dict):
    global name_to_cats, g, ginv
    cats = name_to_cats[term]     
    w = np.sum([weight_dict[cat] for cat in cats])/len(cats)
    return w


def get_article_weight_direct(article_id, threshold, article_to_cats, article_id_to_name, cat_id_to_name, cat_id_to_total_leaves):
    cats_id = article_to_cats[article_id]
    title = article_id_to_name[article_id]
    title = title.replace("_", " ")
    n_found = 0
    avg_weight = 0
    for cat_id in cats_id:
        cat_name = cat_id_to_name[cat_id]
        cat_name = cat_name.replace("_", " ")
        if fuzz.ratio(title, cat_name) > threshold:
            print("hit: " + cat_name, cat_id)
            n_found += 1
            avg_weight += cat_id_to_total_leaves[cat_id]
    if n_found:
        avg_weight /= n_found
        return avg_weight
    else:
        return None

def get_article_weight_sibling(article_id, threshold, article_to_cats, article_id_to_name, cat_id_to_name, cat_id_to_total_leaves, cat_to_articles):
    cats_id = article_to_cats[article_id]
    weights = []
    for cat_id in cats_id:
        siblings_id = cat_to_articles[cat_id]
        for sibling_id in siblings_id:
            weight = get_article_weight_direct(sibling_id, threshold, article_to_cats, article_id_to_name, cat_id_to_name, cat_id_to_total_leaves)
            if weight:
                weights.append(weight)
    if len(weights):
        return sum(weights) / len(weights)
    else:
        return None

def get_article_weight(article_id, threshold, article_to_cats, article_id_to_name, cat_id_to_name, cat_id_to_total_leaves, cat_to_articles):
    weight = get_article_weight_direct(article_id, threshold, article_to_cats, article_id_to_name, cat_id_to_name, cat_id_to_total_leaves)
    if not weight:
        weight = get_article_weight_sibling(article_id, threshold, article_to_cats, article_id_to_name, cat_id_to_name, cat_id_to_total_leaves, cat_to_articles)
        if not weight:
            print("miss")
        else:
            print("sibling")
    else:
        print("direct")
    return weight
    
def test(search, term):
    global cat_to_articles, cat_id_to_name, article_id_to_name, cat_id_to_total_leaves, cat_id_to_total_pages
    global term_to_article
    print(term)
    article_id = term_to_article[term]
    return get_article_weight_direct(article_id, 91, article_to_cats, article_id_to_name, cat_id_to_name, cat_id_to_total_leaves)
    
    results = search_article_title(search, term)
    s = 0
    s_score = 0
    for r in results:
        score, article_id, title, cat_list = r
        s_score += score
        weight = get_article_weight(article_id, 91, article_to_cats, article_id_to_name, cat_id_to_name, cat_id_to_total_leaves, cat_to_articles)
        if weight:
            s += score * weight
    if s:
        s = s/len(results)/s_score
    return s

# generate_data()
# exit()

cat_id_to_name = load_obj("cat_id_to_name.txt")
# # cat_name_to_id = load_obj("cat_name_to_id.txt")
# cat_id_to_pages = load_obj("cat_id_to_pages.txt")
article_id_to_name = load_obj("article_id_to_name.txt")
article_to_cats = load_obj("article_to_cats.txt")
cat_to_articles = load_obj("cat_to_articles.txt")

# g = load_obj("g.txt")
# ginv = load_obj("ginv.txt")
# # # precompute_data(g)
cat_id_to_total_pages = load_obj("id_to_total_pages.txt")
cat_id_to_total_leaves = load_obj("id_to_total_leaves.txt")


# print([cat_id_to_total_leaves[term] for term in ["106923", "98333", "106883"]])
# exit()
# c = 0
# for k,v in article_id_to_name.items():
#     print(k, v)
#     c += 1
#     if c == 20:
#         exit()

es = Elasticsearch()
search = Search(using=es, index="es-capacity", doc_type="article")

terms1 = ["Cat", "Dog", "Bird", "Plant", "Animal"]
terms2 = ["Algorithm", "Database", "Data management", "Data mining", "Computer science"]
terms3 = ["Query language", "Database", "Data management", "Data mining", "Big data", "Computer science"]
terms4 = ["Database", "Theoretical computer science", "Computer vision", "Natural language processing" , "Speech recognition", "Computational linguistics"]
terms5 = ["Champaign", "Chicago", "New York", "Beijing", "Paris", "Illinois", "California", "United States", "France"]

terms_list = [terms2, terms3, terms4, terms5]

term_to_article = {"Algorithm": "3733315",
"Database": "40423634", "Data management": "1015323",
"Data mining": "38062867", "Computer science": "25031924",
"Query language": "3961120",
"Big data": "48151899",
"Computational linguistics": "38562059",
"Speech recognition": "38562215",
"Natural language processing": "43779661",
"Computer vision": "3966765",
"Theoretical computer science": "17326466",
"France": "37407566",
"United States": "33014499",
"California": "7375185",
"Illinois": "11956271",
"Paris": "4244049",
"Beijing": "37299941",
"New York": "51584461",
"Chicago": "12799998",
"Champaign": "8674577"}

if False:
    term1 = input("Enter Term 1:")
    term2 = input("Enter Term 2:")
    while term1:
        term1 = term1.strip()
        term2 = term2.strip()
        if term1 == "exit":
            exit()
        terms = [term1, term2]
        weights = np.array([get_article_weight_gen(search, term, id_to_total_leaves , None) for term in terms])
        plot(terms, weights)
        print("------------")
        print(terms)
        print(weights)
        print("------------")
        if weights[0] > weights[1]:
            print(term1 , ">", term2)
        elif weights[0] < weights[1]:
            print(term1 , "<", term2)
        else:
            print(term1 , "=", term2)
        term1 = input("Enter Term 1:")
        term2 = input("Enter Term 2:")
    exit()

for terms in terms_list:
    # weights = [get_article_weight_gen(search, term, id_to_total_leaves, None) for term in terms]
    # weights1 = [get_article_avg_weight(search, g, term) for term in terms]
    # weights2 = [get_article_weight_gen(search, term, get_category_weight, [g]) for term in terms]
    # weights3 = [get_article_weight_gen(search, term, get_category_norm_weight, [g, ginv]) for term in terms]
    # weights4 = [get_article_weight_gen(search, term, get_category_pages_weight, [g, ginv, cat_id_to_pages]) for term in terms]
    # weights5 = [get_article_weight_gen(search, term, get_category_pages_norm_weight, [g, ginv, cat_id_to_pages]) for term in terms]
    # weights6 = np.array([get_article_weight_gen(search, term, get_category_pre_pages_norm_weight, [g, ginv, id_to_total_pages]) for term in terms])
    # weights7 = np.array([get_article_weight_gen(search, term, id_to_total_pages, None) for term in terms])
    # weights8 = np.array([get_article_weight_gen(search, term, id_to_total_leaves , None) for term in terms])
    # weights9 = np.array([test(term, id_to_total_leaves) for term in terms])
    # weights = weights6**0.7 * weights7**0.3
    
    weights = np.array([test(search, term) for term in terms])
    print("------------")
    print(terms)
    print(weights)
    print("------------")
    plot(terms, weights)