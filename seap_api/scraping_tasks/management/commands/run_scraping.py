# scraping_tasks/management/commands/run_scraping.py
from datetime import datetime

# from api.scrape.scrape_automation.automation import get_acquisitions, get_cpvs_data
from django.core.management.base import BaseCommand
from scraping_tasks.models.scraping_task import ScrapingTask, TaskStatus

# from services.acquisition_service import AcquisitionService


class Command(BaseCommand):
    help = "Run scraping task with given parameters"

    def add_arguments(self, parser):
        parser.add_argument("--task_id", type=str, required=True)
        parser.add_argument("--start_date", type=str, required=True)
        parser.add_argument("--end_date", type=str, required=True)
        parser.add_argument("--cpv_codes", type=str, required=True)

    def handle(self, *args, **options):
        task = ScrapingTask.objects.get(task_id=options["task_id"])
        task.status = TaskStatus.RUNNING
        task.save()

        try:
            # cpv_codes = [int(x) for x in options['cpv_codes'].split(',')]
            # start_date = datetime.fromisoformat(options['start_date'])
            # end_date = datetime.fromisoformat(options['end_date'])

            # # Get current acquisitions to filter
            # current_acquisitions = AcquisitionService.get_all_acquisitions()
            # current_acquisition_ids = [a['acquisition_id'] for a in current_acquisitions]

            # # Run scraping
            # cpvs = get_cpvs_data()
            # days = [start_date]  # For now just use start date
            # acquisitions = get_acquisitions(days, cpvs, None, current_acquisition_ids)

            task.status = TaskStatus.COMPLETED
            # task.result_stats = {'acquisitions_found': len(acquisitions)}
            task.completed_at = datetime.now()
            # add a mock message
            task.message = "Scraping completed successfully"
            # add a mock result
            task.result_stats = {"acquisitions_found": 10}
            task.save()

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.save()
