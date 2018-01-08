import MySQLdb
import pickle
import matplotlib.pyplot as plt

def store_obj(obj, filename):
    with open(filename, "wb") as f:
        pickle.dump(obj, f)

def load_obj(filename):
    with open(filename, "rb") as f:
        obj = pickle.load(f)
    return obj

def generate_data():
    print ("connect db")
    db = MySQLdb.connect(host="localhost",    # your host, usually localhost
                         user="root",         # your username
                         passwd="keepcalm",  # your password
                         db="exp")        # name of the data base

    # you must create a Cursor object. It will let
    #  you execute all the queries you need
    cur = db.cursor()
    # Use all the SQL you like
    cur.execute("SELECT * FROM wiki_cat")
    # print all the first cell of all the rows
    name_to_id = {}
    id_to_name = {}
    g = {}
    all_id = set()
    sub_id = set()

    for row in cur.fetchall():
        c_id = row[0]
        c_name = row[1]
        all_id.add(c_id)
        id_to_name[c_id] = c_name
        name_to_id[c_name] = c_id

    cur.execute("SELECT * FROM wiki_taxonomy")
    for row in cur.fetchall():
        p_id = row[0]
        c_id = row[1]
        sub_id.add(c_id)
        if p_id not in g:
            g[p_id] = [c_id]
        else:
            g[p_id].append(c_id)

    root_id = all_id - sub_id
    # print(map(id_to_name.get, root_id))
    store_obj(name_to_id, "name_to_id.txt")
    store_obj(id_to_name, "id_to_name.txt")
    store_obj(g, "g.txt")
    db.close()

def get_num_leaves(g, nid):
    visited = set()
    return get_num_leaves_support(g, nid, visited)

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

# generate_data()
id_to_name = load_obj("id_to_name.txt")
def get_num_children_support(g, nid, visited):
    visited.add(nid)
    # print (id_to_name[nid],)
    if nid not in g:
        return 1
    s = 0
    for i in g[nid]:
        if i not in visited:
            s += get_num_children_support(g, i, visited)
    return s + 1



name_to_id = load_obj("name_to_id.txt")
g = load_obj("g.txt")


terms = ["Champaign, Illinois", "Chicago", "New York City", "Beijing", "Paris", "Illinois", "California", "United States", "France"]
terms = ["Cats", "Dogs", "Birds", "Plants", "Animals"]
terms = ["Query languages", "Databases", "Data management", "Data mining", "Big data", "Computer science"]
terms = ["Algorithms", "Databases", "Data management", "Data mining", "Computer science"]
terms = ["Databases", "Theoretical computer science", "Computer vision", "Natural language processing" , "Speech recognition", " Computational linguistics"]

ids = [name_to_id.get(term) for term in terms]

rtl = [get_num_leaves(g, i) for i in ids]
rtc = [get_num_children(g, i) for i in ids]
rtd = [get_max_depth(g, i) for i in ids]

def printl(lst):
    for i in lst:
        print(i, "\t", end='')
    print()

print(terms)
printl(terms)
printl(rtl)
printl(rtc)
printl(rtd)



# kc = {"Data retrieval":["Database management systems", "Relational database management systems"], \
#     "PageRank": ["Google Search", "Search engine optimization"], \
#     "User profile": ["Identity management", "Knowledge representation"], \
#     "Schema matching": ["Databases"], \
#     "Relational database management system": ["Relational database management system"],\
#     "Boolean conjunctive query": ["Boolean algebra"],\
#     "Web search query": ["Internet search"],\
#     "Query optimization": ["Database management systems", "Database algorithms"]}

# kc_quant = {}

# for key, val in kc.items():
#     ids = [name_to_id.get(term) for term in val]
#     rtc = [get_num_children(g, i) for i in ids]
#     print(key)
#     print(val)
#     print(rtc)
#     avg = sum(rtc)/len(rtc)
#     kc_quant[key] = avg

# print(kc_quant)



# pos = list(range(len(terms)))
# width = 0.25 

# plt.figure(0)
# _, ax =  plt.subplots()
# plt.bar(pos, rtc, width, label="total num of children") 
# ax.set_xticks([p + 1.5 * width for p in pos])
# ax.set_xticklabels(terms)
# plt.legend(loc='upper right')

# plt.figure(1)
# _, ax =  plt.subplots()
# plt.bar(pos, rtd, width, label="max depth") 
# ax.set_xticks([p + 1.5 * width for p in pos])
# ax.set_xticklabels(terms)
# plt.legend(loc='upper right')

# plt.show()




