# scraping_tasks/management/commands/run_scraping.py
import logging
import os
from collections.abc import Sequence
from datetime import datetime, timedelta
from logging import FileHandler, Formatter

from api.scrape.acquisition_fetcher import AcquisitionFetcher
from api.services.acquisition_service import AcquisitionService
from django.core.management.base import BaseCommand
from scraping_tasks.models.scraping_task import ScrapingTask, TaskStatus


class Command(BaseCommand):
    help = "Run scraping task with given parameters"

    def __init__(self):
        super().__init__()
        self.logger = self._setup_logger()

    def _setup_logger(self):
        """Configure custom logger for the scraping command"""
        # Create logger
        logger = logging.getLogger("run_scraping")
        logger.setLevel(logging.INFO)

        # Create logs directory if it doesn't exist
        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        # Create file handler
        log_file = os.path.join(
            logs_dir, f'scraping_{datetime.now().strftime("%Y%m%d")}.log'
        )
        handler = FileHandler(log_file)
        handler.setLevel(logging.INFO)

        # Create formatter
        formatter = Formatter(
            "%(asctime)s - %(module)s.%(funcName)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)
        return logger

    def add_arguments(self, parser):
        parser.add_argument("--task_id", type=str, required=True)
        parser.add_argument("--start_date", type=str, required=True)
        parser.add_argument("--end_date", type=str, required=True)
        parser.add_argument("--cpv_codes", type=str, required=True)

    def handle(self, *args, **options):
        task = ScrapingTask.objects.get(task_id=options["task_id"])
        task.status = TaskStatus.RUNNING
        task.save()
        self.logger.info(f"Starting scraping task {task.task_id}")

        try:
            cpv_codes = [int(x) for x in options["cpv_codes"].split(",")]
            start_date = datetime.fromisoformat(options["start_date"])
            end_date = datetime.fromisoformat(options["end_date"])

            self.logger.info(
                f"Parameters: CPV codes={cpv_codes}, start={start_date}, end={end_date}"
            )

            # Create date range
            days = self._create_date_range(start_date, end_date)
            self.logger.info(f"Scraping days: {days}")

            # Get current acquisitions to filter
            current_acquisitions = AcquisitionService.get_all_acquisitions()
            current_acquisition_ids = [
                a["acquisition_id"] for a in current_acquisitions
            ]
            self.logger.info(
                f"Found {len(current_acquisition_ids)} current acquisitions"
            )

            # Run scraping
            acquisitions_found, acquisitions_inserted = self._get_acquisitions_for_days(
                task, days, cpv_codes, current_acquisition_ids
            )
            self.logger.info(
                f"Scraping completed. Found {len(acquisitions_found)} acquisitions, inserted {len(acquisitions_inserted)}"
            )

            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.message = "Scraping completed successfully. Found {} acquisitions, inserted {} new acquisitions".format(
                len(acquisitions_found), len(acquisitions_inserted)
            )
            task.save()

        except Exception as e:
            self.logger.error(f"Scraping failed: {e}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.save()

    def _create_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> Sequence[datetime]:
        """
        Creates a list of dates for days between start_date and end_date (inclusive)

        Args:
            start_date (datetime): Starting date
            end_date (datetime): Ending date

        Returns:
            Sequence[datetime]: List of dates
        """
        if start_date > end_date:
            raise ValueError("start_date cannot be after end_date")

        dates = []
        current_date = start_date

        while current_date <= end_date:
            dates.append(current_date)
            current_date += timedelta(days=1)

        return dates

    def _get_acquisitions_for_day_and_cpv(
        self, acquisition_fetcher: AcquisitionFetcher, day: datetime, cpv_id: int
    ):
        self.logger.info(f"Trying to fetch acquisitions for day {day} and CPV {cpv_id}")

        fetched_acquisitions = acquisition_fetcher.get_all_acquisitions_data(
            day, day, cpv_code_id=cpv_id
        )
        return fetched_acquisitions

    def _get_acquisitions_for_days(
        self,
        current_task: ScrapingTask,
        days: Sequence[datetime],
        cpvs: Sequence[int],
        current_acquisitions_ids: Sequence[int],
    ):
        acquisition_fetcher = AcquisitionFetcher()
        total_acquisitions_found = []
        total_acquisitions_inserted = []
        stats = {}
        self.logger.info(f"Processing {len(days)} days")
        for index, day in enumerate(days):
            self.logger.info(f"Processing day {day}")
            day_key = day.strftime("%Y-%m-%d")
            acquisitions = []
            for cpv in cpvs:
                acquisitions += self._get_acquisitions_for_day_and_cpv(
                    acquisition_fetcher, day, cpv
                )

            self.logger.info(f"Found {len(acquisitions)} acquisitions for day {day}")
            stats[f"day_{day_key}_total"] = len(acquisitions)
            total_acquisitions_found += acquisitions

            # Filter out already existing acquisitions
            acquisitions = [
                a
                for a in acquisitions
                if a["directAcquisitionID"] not in current_acquisitions_ids
            ]
            self.logger.info(
                f"Filtered out {len(total_acquisitions_found) - len(acquisitions)} existing acquisitions"
            )
            # Insert acquisitions
            for to_insert in acquisitions:
                AcquisitionService.create_acquisition_with_items(
                    acquisition_data=to_insert,
                    items_data=to_insert["directAcquisitionItems"],
                )
            self.logger.info(f"Inserted {len(acquisitions)} acquisitions")
            total_acquisitions_inserted += acquisitions
            stats[f"day_{day_key}_inserted"] = len(acquisitions)
            current_task.progress = (index + 1) / len(days) * 100
            current_task.result_stats = stats
            current_task.save()

        stats["total_acquisitions_found"] = len(total_acquisitions_found)
        stats["total_acquisitions_inserted"] = len(total_acquisitions_inserted)

        current_task.result_stats = stats
        current_task.progress = 100
        current_task.save()

        return total_acquisitions_found, total_acquisitions_inserted
