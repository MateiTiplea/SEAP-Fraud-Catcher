import json

import pandas as pd
import tabula


def read_pdf_to_dataframe(pdf_path):
    return tabula.read_pdf(
        pdf_path, pages="all", multiple_tables=True, encoding="utf-8"
    )


def get_filtered_classes(json_path):
    fin = open(json_path, "r", encoding="utf-8")
    json_content = json.load(fin)
    fin.close()

    return json_content


def dump_json(json_content, dump_path):
    fout = open(dump_path, "w", encoding="utf-8")
    json.dump(json_content, fout, indent=4, ensure_ascii=False)
    fout.close()


def find_cpvs_for_standard_class(pdf_data, standard_class):
    # find all cpv_codes from the first column of each table that has the value from the 4th column equal to the standard class
    cpv_codes = set()

    for table in pdf_data:
        if len(table.columns) <= 3:
            continue

        for index, row in table.iterrows():
            if len(row) < 4:
                continue
            if pd.notnull(row[3]):
                table_class = " ".join(row[3].splitlines()).strip()
                if table_class == standard_class:
                    cpv_codes.add(row[0].strip())

    return list(cpv_codes)


def main():
    pdf_tables = read_pdf_to_dataframe("Reclasificare-coduri-CPV.pdf")

    filtered_classes = get_filtered_classes("filtered_standardized_classes.json")

    filtered_cpvs_for_classes = dict()
    for fclass in filtered_classes:
        filtered_cpvs_for_classes[fclass] = find_cpvs_for_standard_class(
            pdf_tables, fclass
        )

    dump_json(filtered_cpvs_for_classes, "filtered_cpv_codes_for_classes.json")


if __name__ == "__main__":
    main()
