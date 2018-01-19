
map_subcat_to_cat = True
map_cat_to_subcat = True
map_article_to_cat = True
map_article_to_cat2 = True
map_cat_id = {}
map_article_id = {}

with open("data/cat_id_to_cat_title.txt", "r", encoding = "utf-8") as fin:
    for line in fin.readlines():
        sp = line.split("\t")
        map_cat_id[sp[1].strip()] = sp[0].strip() 

if map_subcat_to_cat:
    file_in = "data/subcat_title_to_cat_title.txt"
    file_out = "data/subcat_id_to_cat_id.txt"
    fin = open(file_in, "r", encoding = "utf-8")
    fout = open(file_out, "w", encoding = "utf-8")
    line = fin.readline()
    c = 0
    while line:
        sp = line.split("\t")
        try:
            subcat_id = map_cat_id[sp[0].strip()]
            cat_id = map_cat_id[sp[1].strip()]
            fout.write(subcat_id + "\t" + cat_id + "\n")
        except:
            c += 1
        line = fin.readline()
    fin.close()
    fout.close()
    print("missed", c)
    print("map_subcat_to_cat is done.")

if map_cat_to_subcat:
    file_in = "data/subcat_title_to_cat_title.txt"
    file_out = "data/cat_title_to_subcat_title.txt"
    fin = open(file_in, "r", encoding = "utf-8")
    fout = open(file_out, "w", encoding = "utf-8")
    line = fin.readline()
    c = 0
    while line:
        sp = line.split("\t")
        try:
            subcat_id = map_cat_id[sp[0].strip()]
            cat_id = map_cat_id[sp[1].strip()]
            fout.write(cat_id + "\t" + subcat_id + "\n")
        except:
            c += 1
        line = fin.readline()
    fin.close()
    fout.close()
    print("missed", c)
    print("map_cat_to_subcat is done.")

if map_article_to_cat:
    file_in = "data/article_title_to_cat_title.txt"
    file_out = "data/article_title_to_cat_id.txt"
    fin = open(file_in, "r", encoding = "utf-8")
    fout = open(file_out, "w", encoding = "utf-8")
    line = fin.readline()
    c = 0
    while line:
        sp = line.split("\t")
        try:
            cat_id = map_cat_id[sp[1].strip()]
            fout.write(sp[0].strip() + "\t" + cat_id + "\n")
        except:
            c += 1
        line = fin.readline()
    fin.close()
    fout.close()
    print("missed", c)
    print("map_article_to_cat is done.")


if map_article_to_cat2:
    with open("data/article_id_to_article_title.txt", "r", encoding = "utf-8") as fin:
        for line in fin.readlines():
            sp = line.split("\t")
            map_article_id[sp[1].strip()] = sp[0].strip()
    file_in = "data/article_title_to_cat_id.txt"
    file_out = "data/article_id_to_cat_id.txt"
    fin = open(file_in, "r", encoding = "utf-8")
    fout = open(file_out, "w", encoding = "utf-8")
    line = fin.readline()
    c = 0
    while line:
        sp = line.split("\t")
        try:
            article_id = map_article_id[sp[0].strip()]
            fout.write(article_id + "\t" + sp[1].strip() + "\n")
        except:
            c += 1
        line = fin.readline()
    fin.close()
    fout.close()
    print("missed", c)
    print("map_article_to_cat2 is done.")
