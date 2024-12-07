from abc import ABC, abstractmethod

import requests


class RequestStrategy(ABC):
    @abstractmethod
    def make_request(self, url, headers, body=None):
        pass


class GetRequestStrategy(RequestStrategy):
    def make_request(self, url, headers, body=None):
        return requests.get(url, headers=headers)


class PostRequestStrategy(RequestStrategy):
    def make_request(self, url, headers, body=None):
        return requests.post(url, headers=headers, json=body, verify=True)
