from collections import defaultdict
agg_article_id = False
agg_cat_article = True

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
