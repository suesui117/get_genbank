# !/usr/bin/env python3

"""
Parses GenBank file and outputs preferred transcript GenBank file
"""

import os
import re
import sys
import glob
from Bio import GenBank, Entrez


def parse_path(in_path, user_nm):
    with open(in_path) as fh:
        for record in GenBank.parse(fh):
            try:
                rec = str(record)
                if user_nm not in rec:
                    nm = user_nm.split(".")[0]
                    print("Hello, user_nm not in record")
                    gb_nm = re.search(r"(N[M]_\d+)", Entrez.efetch(db="nuccore", id=nm, rettype="acc", retmode="text").read()).group(0)
                else:
                    gb_nm = re.search(r"(N[M]_\d+)", Entrez.efetch(db="nuccore", id=user_nm, rettype="acc", retmode="text").read()).group(
                        0)

                np = re.search(r"(NP_\d+.\d)", Entrez.efetch(db="nuccore", id=gb_nm, rettype="gb", retmode="text").read()).group(1).split(".")[
                        0]
                nc = re.search(r"(VERSION\s+)(NC_\d+.\d+)", rec).group(2)

            except AttributeError:  # if attributeError, it will be NR RNA accessions, we don't parse, leave as it is
                print("AttributeError" + in_path)
                if "NR_" in user_nm and "NR_" in rec:
                    gb_nm = re.search(r"(N[R]_\d+)", Entrez.efetch(db="nuccore", id=user_nm, rettype="acc", retmode="text").read()).group(
                        0)
                    nc = re.search(r"(VERSION\s+)(NC_\d+.\d+)", rec).group(2)
    return gb_nm, np, nc


def write_outfile(path, gene, unpack):
    with open(path) as fh:
        lst = []
        (gb_nm, np, nc) = unpack

        final_nm = ""
        for record in GenBank.parse(fh):
            for every_chunk in record.features:
                if (gb_nm in str(every_chunk) and gene in str(every_chunk)) or (gene in str(every_chunk) and np.split(".")[0] in str(
                        every_chunk)):
                    lst.append(str(every_chunk))

                    try:
                        final_nm = re.search(r"(N[M|R]_\d+.\d+)", str(every_chunk)).group(0)
                        print(final_nm)
                    except AttributeError:
                        pass

            total = "".join(lst)
            if len(lst) == 0 or len(lst) > 2:
                sys.exit()

            field1_field2 = "".join([str(record.features[0]), str(record.features[1])])
            record.features = field1_field2 + total
            return record, final_nm, nc


def main():
    """The main function of the script."""

    Entrez.email = "suesui117@gmail.com"
    directory = os.getcwd() + "/auto_genbank/"
    final_dir = os.getcwd() + "/completed/"

    while len(os.listdir(directory)) > 1:
        files_path = os.path.join(directory, '*')
        files = sorted(glob.iglob(files_path), key=os.path.getctime, reverse=True)
        for f in files[1:]:
            os.unlink(f)

    for i in os.listdir(directory):
        if i.endswith(".gbk"):
            path = directory + i
            gene = i.split("_")[0]
            user_nm = "_".join([i.split("_")[1], i.split("_")[2]])

            unpack = parse_path(path, user_nm)
            (record, final_nm, nc) = write_outfile(path, gene, unpack)  # This function returns record, final_nm and nc for output writing

            outfile = final_dir + "_".join([gene, final_nm, nc]) + ".gbk"
            with open(outfile, "w") as file:
                file.write(str(record))
                os.remove(path)


if __name__ == "__main__":
    main()

