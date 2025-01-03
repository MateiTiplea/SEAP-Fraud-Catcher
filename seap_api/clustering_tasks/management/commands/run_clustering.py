import logging
import os
from datetime import datetime
from django.core.management.base import BaseCommand
from clustering_tasks.models import ClusteringTask, TaskStatus
from decision_module.fraud_scoring import create_clusters


class Command(BaseCommand):
    """
    Command to run the clustering task in the background
    """
    help = "Run clustering task with given parameters"

    def __init__(self):
        super().__init__()
        self.logger = self._setup_logger()

    # noinspection PyMethodMayBeStatic
    def _setup_logger(self):
        """Configure custom logger for the clustering command"""
        logger = logging.getLogger("run_clustering")
        logger.setLevel(logging.INFO)

        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        # Dynamically create the log file name
        log_file_name = f"clustering_{datetime.now().strftime('%Y%m%d')}.log"
        log_file_path = os.path.join(logs_dir, log_file_name)

        handler = logging.FileHandler(log_file_path)
        handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(module)s.%(funcName)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    def add_arguments(self, parser):
        parser.add_argument("--task_id", type=str, required=True)

    def handle(self, *args, **options):
        task_id = options["task_id"]
        try:
            task = ClusteringTask.objects.get(task_id=task_id)
        except ClusteringTask.DoesNotExist:
            self.logger.error(f"Task with ID {task_id} does not exist.")
            self.stderr.write(f"Task with ID {task_id} does not exist.")
            return
        task.status = TaskStatus.RUNNING
        task.updated_at = datetime.now()
        task.save()
        self.logger.info(f"Starting clustering task {task_id}")

        try:
            self.logger.info("Initiating clustering process")
            create_clusters()  # Invoke your clustering logic here

            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.message = "Clustering completed successfully."
            task.save()
            self.logger.info(f"Clustering task {task_id} completed successfully")

        except Exception as e:
            self.logger.error(f"Clustering failed: {e}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.save()
