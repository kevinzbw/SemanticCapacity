import os.path as path
from collections import defaultdict

DATA_DIR = "new_data/"

def normal_mapping(sp, rt_dict):
    rt_dict[sp[0]] = sp[1]
def reverse_mapping(sp, rt_dict):
    rt_dict[sp[1]] = sp[0]
def aggregate_value1(sp, rt_dict):
    rt_dict[sp[0]].append(sp[1])
def aggregate_value2(sp, rt_dict):
    rt_dict[sp[1]].append(sp[0])
def convert_value2(sp, fout, intp_dict):
    fout.write(sp[0] + "\t" + intp_dict[sp[1]] + "\n")

def file_op(name, file_in, file_out, mapping_func, intp_dict, agg_flag):
    print("Start", name)
    rt_dict = defaultdict(list) if agg_flag else dict()
    file_in_path = path.join(DATA_DIR, file_in)
    fin = open(file_in_path, "r", encoding = "utf-8")
    if file_out:
        file_out_path = path.join(DATA_DIR, file_out)
        fout = open(file_out_path, "w", encoding = "utf-8")
    line = fin.readline()
    c = 0
    while line:
        sp = line.split("\t")
        sp = [v.strip() for v in sp]
        try:
            if file_out:
                mapping_func(sp, fout, intp_dict)
            else:
                mapping_func(sp, rt_dict)
        except:
            c += 1
        line = fin.readline()
    fin.close()
    if file_out:
        fout.close()
    print("Finish;", "Miss:", c)
    return rt_dict

def write_agg_dict(file_out, agg_dict):
    file_out_path = path.join(DATA_DIR, file_out)
    fout = open(file_out_path, "w", encoding = "utf-8")
    for key, value in agg_dict.items():
        fout.write(key+"\t"+value[0])
        if len(value) > 1:
            for v in value[1:]:
                fout.write(";"+v)
        fout.write("\n")
    fout.close()
def write_agg_dict_elastic(file_out, agg_dict, intp_dict):
    c = 0
    file_out_path = path.join(DATA_DIR, file_out)
    fout = open(file_out_path, "w", encoding = "utf-8")
    fout.write("article_id\tarticle_title\tcategory_list\n")
    for key, value in agg_dict.items():
        try:
            title = intp_dict[key].replace("_", " ")
        except:
            c += 1
            continue
        fout.write(key+"\t"+title+"\t"+value[0])
        if len(value) > 1:
            for v in value[1:]:
                fout.write(";"+v)
        fout.write("\n")
    fout.close()
    print("Miss(article id to title):", c)

map_id_to_title = False
agg_id = True

cat_title_to_cat_id = file_op("reading cat info", "page_cat.txt", None, reverse_mapping, None, False)
if agg_id:
    article_id_to_article_title = file_op("Reading page info", "page.txt", None, normal_mapping, None, False)
        
if map_id_to_title:
    file_in = "subcatlink.txt"
    file_out = "subcat_id_to_cat_id.txt"
    file_op("converting subcatlink title", file_in, file_out, convert_value2, cat_title_to_cat_id, False)
    file_in = "pagelink.txt"
    file_out = "article_id_to_cat_id.txt"
    file_op("converting pagelink title", file_in, file_out, convert_value2, cat_title_to_cat_id, False)

if agg_id:
    file_in = "article_id_to_cat_id.txt"
    # agg_cat_id_to_article_id = file_op("aggregating cat id", file_in, None, aggregate_value2, None, True)
    # write_agg_dict("agg_cat_id_to_article_id.txt", agg_cat_id_to_article_id)

    agg_article_id_to_cat_id = file_op("aggregating article id", file_in, None, aggregate_value1, None, True)
    write_agg_dict("agg_article_id_to_cat_id.txt", agg_article_id_to_cat_id)
    # write_agg_dict_elastic("article.txt", agg_article_id_to_cat_id, article_id_to_article_title)
    