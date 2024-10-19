import json
import requests

url = "http://e-licitatie.ro/api-pub/DirectAcquisitionCommon/GetDirectAcquisitionList/"

headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "Referer": "https://e-licitatie.ro/pub/notices/contract-notices/list/0/0"
}

page_index = 0
page_size = 20
all_data = []
has_more_data = True
aquisition_data = "2024-01-03"  # trebuie modificat

while has_more_data:
    body = json.dumps({
        "pageSize": page_size,
        "showOngoingDa": False,
        "cookieContext": None,
        "pageIndex": page_index,
        "sysDirectAcquisitionStateId": None,
        "publicationDateStart": None,
        "publicationDateEnd": None,
        "finalizationDateStart": aquisition_data,
        "finalizationDateEnd": aquisition_data
    })

    response = requests.post(url, headers=headers, data=body)

    if response.status_code == 200:
        data = response.json()
        print(f"Page {page_index + 1}: {len(data.get('items', []))} items")

        all_data.extend(data.get("items", []))
        if len(data.get('items', [])) == 0:
            has_more_data = False
        if "searchTooLong" in data and data["searchTooLong"]:
            page_index += 1
        else:
            has_more_data = False
    else:
        print(f"Error: {response.status_code}")
        has_more_data = False

print(f"Total items retrieved: {len(all_data)}")

file_name = aquisition_data +"_achizitii.json"
with open(file_name, 'w') as f:
    json.dump(all_data, f, indent=2)

print("All data saved to file:", file_name)
