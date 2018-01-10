
files_in = ["sql_article_id_to_article_title.txt", "sql_cat_id_to_cat_title.txt", "sql_cat_full.txt"]
files_out = ["article_id_to_article_title.txt", "cat_id_to_cat_title.txt", "cat_full.txt"]
files = zip(files_in, files_out)
DIR = "data/"
for file_in, file_out in files:
    file_in = DIR + file_in
    file_out = DIR + file_out
    fin = open(file_in, "r", encoding = "latin-1")
    fout = open(file_out, "w", encoding = "utf-8")
    for line in fin.readlines():
        fout.write(line)
    fin.close()
    fout.close()
