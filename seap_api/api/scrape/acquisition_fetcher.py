import json
import os
from datetime import datetime, timedelta

from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout

from aspects.error_handlers import handle_exceptions
from aspects.loggers import log_method_calls
from aspects.validation import validate_types
from scrape.request_strategy import GetRequestStrategy, PostRequestStrategy

ENV_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))


def get_body(
        start_date,
        end_date,
        page_index,
        page_size=20,
        acquisition_state_id=None,
        cpv_code_id=None,
):
    body = {
        "pageSize": page_size,
        "showOngoingDa": False,
        "pageIndex": page_index,
        "finalizationDateStart": start_date.strftime("%Y-%m-%d"),
        "finalizationDateEnd": end_date.strftime("%Y-%m-%d"),
    }
    if acquisition_state_id:
        body["sysDirectAcquisitionStateId"] = acquisition_state_id
    if cpv_code_id:
        body["cpvCodeId"] = cpv_code_id
    return json.dumps(body)


def get_acquisitions_ids(acquisitions):
    return [acquisition["directAcquisitionId"] for acquisition in acquisitions]


class AcquisitionFetcher:
    API_DICT = {
        "acquisition": {
            "url": "http://e-licitatie.ro/api-pub/DirectAcquisitionCommon/GetDirectAcquisitionList/",
            "method": "POST",
        },
        "view": {
            "url": "http://e-licitatie.ro/api-pub/PublicDirectAcquisition/getView/{acquisition_id}",
            "method": "GET",
        },
    }

    def __init__(self):
        self.headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "Referer": "https://e-licitatie.ro/pub/notices/contract-notices/list/0/0",
        }
        self.request_strategies = {
            "GET": GetRequestStrategy(),
            "POST": PostRequestStrategy(),
        }

    @log_method_calls
    @handle_exceptions(
        error_types=(HTTPError, Timeout, ConnectionError, RequestException),
        num_retries=3,
        reraise=True
    )
    @validate_types
    def call_api(self, url: str, method: str, body: dict = None):
        """
        Makes an API call using the appropriate request strategy.

        Parameters:
        -----------
        url : str
            The URL to make the request to
        method : str
            The HTTP method to use
        body : dict, optional
            The request body data

        Returns:
        --------
        tuple
            A tuple containing (response, message)
        """
        strategy = self.request_strategies.get(method)
        if not strategy:
            message = f"Error: HTTP method {method} is not supported for this url:{url}."
            return [None, message]

        response = strategy.make_request(url, headers=self.headers, body=body)
        response.raise_for_status()  # Raise an error for HTTP status codes 4xx/5xx
        return [response, "Success"]

    @log_method_calls
    @handle_exceptions(error_types=(ValueError, KeyError))
    @validate_types
    def fetch_data_for_one_day(
            self,
            finalization_day: datetime,
            page_size: int = 200,
            cpv_code_id: int = None,
            acquisition_state_id: int = None,
    ):
        page_index = 0
        has_more_data = True
        acquisitions = []

        while has_more_data:
            body = get_body(
                finalization_day,
                finalization_day,
                page_index,
                page_size,
                acquisition_state_id,
                cpv_code_id,
            )
            body = dict(body=json.loads(body))
            response, message = self.call_api(
                self.API_DICT["acquisition"]["url"],
                self.API_DICT["acquisition"]["method"],
                body=body,
            )

            if message == "Success":
                data = response.json()
                page = data.get("items", [])
                acquisitions.extend(page)
                has_more_data = len(page) > 0
                page_index += 1
            else:
                has_more_data = False
        return acquisitions

    @log_method_calls
    @handle_exceptions(error_types=(ValueError, KeyError))
    @validate_types
    def fetch_data_from_acquisitions(
            self,
            finalization_date_start: datetime,
            finalization_date_end: datetime,
            page_size: int = 200,
            acquisition_state_id: int = 7,
            cpv_code_id: int = None,
    ):
        all_acquisitions = []

        current_day = finalization_date_start
        while current_day <= finalization_date_end:
            daily_acquisitions = self.fetch_data_for_one_day(
                finalization_day=current_day,
                page_size=page_size,
                cpv_code_id=cpv_code_id,
                acquisition_state_id=acquisition_state_id,
            )
            all_acquisitions.extend(daily_acquisitions)

            current_day += timedelta(days=1)

        return all_acquisitions

    @log_method_calls
    @handle_exceptions(error_types=(ValueError, KeyError))
    @validate_types
    def fetch_data_from_view(self, acquisition_id: int):
        url = self.API_DICT["view"]["url"].format(acquisition_id=acquisition_id)
        response, message = self.call_api(url, self.API_DICT["view"]["method"])
        if message == "Success":
            return response.json()
        else:
            print(message)
            return None

    @log_method_calls
    @handle_exceptions(error_types=(ValueError, KeyError))
    @validate_types
    def get_all_acquisitions_data(
            self,
            finalization_date_start: datetime,
            finalization_date_end: datetime,
            acquisition_state_id: int = 7,
            cpv_code_id: int = None,
    ):
        acquisitions = self.fetch_data_from_acquisitions(
            finalization_date_start=finalization_date_start,
            finalization_date_end=finalization_date_end,
            acquisition_state_id=acquisition_state_id,
            cpv_code_id=cpv_code_id,
        )
        acquisitions_ids = get_acquisitions_ids(acquisitions)
        acquisitions_full_data = []
        for acquisition_id in acquisitions_ids:
            view_data = self.fetch_data_from_view(acquisition_id)
            if view_data:
                acquisitions_full_data.append(view_data)
        return acquisitions_full_data
