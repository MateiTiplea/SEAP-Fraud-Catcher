from locust import HttpUser, task, between


class SEAPApiUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def list_acquisitions(self):
        self.client.get("/api/v1/acquisitions/")

    @task
    def list_acquisition_by_id(self):
        self.client.get("/api/v1/acquisitions/118375829")
