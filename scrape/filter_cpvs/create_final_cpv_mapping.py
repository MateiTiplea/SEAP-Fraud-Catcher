import json


def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.readlines()


def read_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def dump_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def process_full_cpv_list(full_cpv_list):
    full_cpv_mapping = {}
    for line in full_cpv_list:
        seap_cpv_id, cpv_text = line.split("|", maxsplit=1)
        cpv_text = cpv_text.strip()
        seap_cpv_id = seap_cpv_id.strip()

        cpv_code = cpv_text.split(" ")[0].strip()
        cpv_description = cpv_text.split(" ", maxsplit=1)[1].strip()

        full_cpv_mapping[cpv_code] = {
            "seap_cpv_id": seap_cpv_id,
            "cpv_code": cpv_code,
            "cpv_description": cpv_description,
            "cpv_text": cpv_text,
        }

    return full_cpv_mapping


def create_cpv_mapping(minimal_mapping, full_cpv_mapping):
    result = dict()

    for category in minimal_mapping:
        result[category] = list()
        for cpv_code in minimal_mapping[category]:
            if cpv_code in full_cpv_mapping:
                result[category].append(full_cpv_mapping[cpv_code])

    return result


def main():
    minimal_mapping = read_json("filtered_cpv_codes_for_classes.json")
    full_cpv_list = read_file("cpvs.txt")
    full_cpv_mapping = process_full_cpv_list(full_cpv_list)

    final_cpv_mapping = create_cpv_mapping(minimal_mapping, full_cpv_mapping)
    dump_json("final_cpv_mapping.json", final_cpv_mapping)


if __name__ == "__main__":
    main()
