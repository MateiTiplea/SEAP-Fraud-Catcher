from dateutil import parser

ACQUISITION_MAPPING = {
    "directAcquisitionID": "acquisition_id",
    "directAcquisitionName": "name",
    "directAcquisitionDescription": "description",
    "uniqueIdentificationCode": "identification_code",
    "publicationDate": "publication_date",
    "finalizationDate": "finalization_date",
    "cpvCodeID": "cpv_code_id",
    "cpvCode": "cpv_code_text",
}

ITEM_MAPPING = {
    "catalogItemName": "name",
    "catalogItemDescription": "description",
    "itemMeasureUnit": "unit_type",
    "itemQuantity": "quantity",
    "itemClosingPrice": "closing_price",
    "cpvCodeID": "cpv_code_id",
    "cpvCode": "cpv_code_text",
}


def filter_acquisition_data(acquisition_data):
    fields_to_keep = [
        "directAcquisitionID",
        "directAcquisitionName",
        "directAcquisitionDescription",
        "uniqueIdentificationCode",
        "publicationDate",
        "finalizationDate",
    ]
    filtered_data = {
        ACQUISITION_MAPPING[key]: acquisition_data[key]
        for key in fields_to_keep
        if key in acquisition_data
    }
    if "publication_date" in filtered_data:
        filtered_data["publication_date"] = parser.isoparse(
            filtered_data["publication_date"]
        )
    if "finalization_date" in filtered_data:
        filtered_data["finalization_date"] = parser.isoparse(
            filtered_data["finalization_date"]
        )
    if "cpvCode" in acquisition_data:
        filtered_data["cpv_code_id"] = acquisition_data["cpvCode"]["id"]
        filtered_data["cpv_code_text"] = "{} - {}".format(
            acquisition_data["cpvCode"]["localeKey"],
            acquisition_data["cpvCode"]["text"],
        )
    return filtered_data


def filter_item_data(item_data):
    fields_to_keep = [
        "catalogItemName",
        "catalogItemDescription",
        "itemMeasureUnit",
        "itemQuantity",
        "itemClosingPrice",
    ]
    filtered_data = {
        ITEM_MAPPING[key]: item_data[key] for key in fields_to_keep if key in item_data
    }
    if "cpvCode" in item_data:
        filtered_data["cpv_code_id"] = item_data["cpvCode"]["id"]
        filtered_data["cpv_code_text"] = "{} - {}".format(
            item_data["cpvCode"]["localeKey"], item_data["cpvCode"]["text"]
        )
    if "directAcquisitionID" in item_data:
        filtered_data["acquisition"] = item_data["directAcquisitionID"]
    return filtered_data
