from collections import defaultdict
agg_article_id = False
agg_article_id2 = True
agg_cat_article = False

if agg_article_id:
    agg = defaultdict(list)
    file_in = "data/article_title_to_cat_id.txt"
    file_out = "data/agg_article_title_to_cat_id.txt"
    fin = open(file_in, "r", encoding = "ISO-8859-1")
    line = fin.readline()
    while line:
        sp = line.split("\t")
        article = sp[0].strip().replace("_", " ")
        cat = sp[1].strip()
        agg[article].append(cat)
        line = fin.readline()
    fin.close()
    fout = open(file_out, "w")
    fout.write("title\tcategories\n")
    for article, cats in agg.items():
        fout.write(article + "\t" + cats[0])
        if len(cats) > 1:
            for cat in cats[1:]:
                fout.write(";" + cat)
        fout.write("\n")
    fout.close()
    print("agg_article_id is done.")

if agg_article_id2:
    map_article_id = {}
    with open("data/official_article_id_to_article_title.txt", "r", encoding = "ISO-8859-1") as fin:
        for line in fin.readlines():
            sp = line.split("\t")
            map_article_id[sp[0].strip()] = sp[1].strip()
    agg = defaultdict(list)
    file_in = "data/article_id_to_cat_id.txt"
    file_out = "data/article.txt"
    fin = open(file_in, "r", encoding = "ISO-8859-1")
    line = fin.readline()
    while line:
        sp = line.split("\t")
        article = sp[0].strip()
        cat = sp[1].strip()
        agg[article].append(cat)
        line = fin.readline()
    fin.close()
    fout = open(file_out, "w")
    fout.write("article_id\tarticle_title\tcategories\n")
    for article_id, cats in agg.items():
        article_title = map_article_id[article_id].replace("_", " ")
        fout.write(article_id + "\t" + article_title + "\t" + cats[0])
        if len(cats) > 1:
            for cat in cats[1:]:
                fout.write(";" + cat)
        fout.write("\n")
    fout.close()
    print("agg_article_id2 is done.")

if agg_cat_article:
    agg = defaultdict(list)
    file_in = "data/article_id_to_cat_id.txt"
    file_out = "data/agg_cat_id_to_article_id.txt"
    fin = open(file_in, "r", encoding = "ISO-8859-1")
    line = fin.readline()
    while line:
        sp = line.split("\t")
        article = sp[0].strip()
        cat = sp[1].strip()
        agg[cat].append(article)
        line = fin.readline()
    fin.close()
    fout = open(file_out, "w")
    # fout.write("title\tcategories\n")
    for cat, articles in agg.items():
        fout.write(cat + "\t" + articles[0])
        if len(articles) > 1:
            for article in articles[1:]:
                fout.write(";" + article)
        fout.write("\n")
    fout.close()
    print("agg_cat_article is done.")
