import json
from datetime import datetime, timedelta

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
start_time = datetime.strptime("2024-01-05 00:00:00", "%Y-%m-%d %H:%M:%S")
end_time = datetime.strptime("2024-01-05 23:59:59", "%Y-%m-%d %H:%M:%S")
time_interval = timedelta(hours=1)

while start_time < end_time:
    page_index = 0
    next_time = min(start_time + time_interval, end_time)
    has_more_data = True
    finalization_date_start = start_time.strftime("%Y-%m-%dT%H:%M:%S+02:00")
    finalization_date_end = next_time.strftime("%Y-%m-%dT%H:%M:%S+02:00")
    print(f"Getting data for {finalization_date_start} - {finalization_date_end}")
    while has_more_data:
        body = json.dumps({
            "pageSize": page_size,
            "showOngoingDa": False,
            "cookieContext": None,
            "pageIndex": page_index,
            "sysDirectAcquisitionStateId": None,
            "publicationDateStart": None,
            "publicationDateEnd": None,
            "finalizationDateStart": finalization_date_start,
            "finalizationDateEnd": finalization_date_end
        })

        response = requests.post(url, headers=headers, data=body)

        if response.status_code == 200:
            data = response.json()
            print(f"Page {page_index + 1}: {len(data.get('items', []))} items")
            for item in data.get("items", []):
                print(f"  - {item['finalizationDate']}")

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
    start_time = next_time

print(f"Total items retrieved: {len(all_data)}")

file_name = start_time.strftime("%Y-%m-%d") + "_achizitii.json"
with open(file_name, 'w') as f:
    json.dump(all_data, f, indent=2)

print("All data saved to file:", file_name)
