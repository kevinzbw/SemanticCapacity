
clean_subcat_to_cat = True
clean_article_to_cat = True

if clean_subcat_to_cat:
    file_in = "data/skos_categories_en.txt"
    file_out = "data/subcat_title_to_cat_title.txt"
    fin = open(file_in, "r", encoding="utf-8")
    fout = open(file_out, "w", encoding="utf-8")
    line = fin.readline()
    while line:
        if not line.startswith("<"):
            line = fin.readline()
            continue
        space1 = line.find(">")+1
        rel = line[line.find("#", space1)+1:]
        if not rel.startswith("broader"):
            line = fin.readline()
            continue
        child = line[0:space1]
        child = child[child.rfind(":")+1:-1]
        parent = rel[rel.rfind(":")+1:rel.rfind(">")]
        fout.write(child + "\t" + parent + "\n")
        line = fin.readline()
    fin.close()
    fout.close()
    print("clean_subcat_to_cat is done.")

if clean_article_to_cat:
    file_in = "data/article_categories_en.txt"
    file_out = "data/article_title_to_cat_title.txt"
    fin = open(file_in, "r", encoding="utf-8")
    fout = open(file_out, "w", encoding="utf-8")
    line = fin.readline()
    while line:
        if not line.startswith("<"):
            line = fin.readline()
            continue
        space1 = line.find(">")+1
        article = line[0:space1]
        article = article[article.rfind("/")+1:-1]
        category = line[line.rfind(":")+1:line.rfind(">")]
        fout.write(article + "\t" + category + "\n")
        line = fin.readline()
    fin.close()
    fout.close()
    print("clean_article_to_cat is done.")