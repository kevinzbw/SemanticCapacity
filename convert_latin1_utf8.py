import os
DATA_DIR = "new_data/"
for file in os.listdir(DATA_DIR):
    if file.startswith("sql") and file.endswith(".txt"):
        file_in = os.path.join(DATA_DIR, file)
        file_out = os.path.join(DATA_DIR, file[4:])
        print("Converting " + file_in)
        fin = open(file_in, "r", encoding = "latin-1")
        fout = open(file_out, "w", encoding = "utf-8")
        for line in fin.readlines():
            fout.write(line)
        fin.close()
        fout.close()