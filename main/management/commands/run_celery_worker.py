"""
Management command to run Celery workers with different queue configurations.
"""
from django.core.management.base import BaseCommand
import subprocess
import sys


class Command(BaseCommand):
    help = 'Run Celery workers with different queue configurations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--worker-type',
            type=str,
            choices=['all', 'pdf', 'email', 'analysis', 'notification', 'cleanup', 'statistics'],
            default='all',
            help='Type of worker to run'
        )
        parser.add_argument(
            '--concurrency',
            type=int,
            default=2,
            help='Number of concurrent workers'
        )
        parser.add_argument(
            '--loglevel',
            type=str,
            default='info',
            choices=['debug', 'info', 'warning', 'error', 'critical'],
            help='Log level'
        )

    def handle(self, *args, **options):
        worker_type = options['worker_type']
        concurrency = options['concurrency']
        loglevel = options['loglevel']

        if worker_type == 'all':
            self.run_all_workers(concurrency, loglevel)
        else:
            self.run_specific_worker(worker_type, concurrency, loglevel)

    def run_all_workers(self, concurrency, loglevel):
        """Run workers for all queues."""
        self.stdout.write(
            self.style.SUCCESS('Starting Celery worker for all queues...')
        )
        
        cmd = [
            'celery', '-A', 'CVProject', 'worker',
            '--loglevel', loglevel,
            '--concurrency', str(concurrency),
            '--queues', 'default,pdf_queue,email_queue,analysis_queue,notification_queue,cleanup_queue,statistics_queue'
        ]
        
        self.run_command(cmd)

    def run_specific_worker(self, worker_type, concurrency, loglevel):
        """Run worker for specific queue."""
        queue_map = {
            'pdf': 'pdf_queue',
            'email': 'email_queue',
            'analysis': 'analysis_queue',
            'notification': 'notification_queue',
            'cleanup': 'cleanup_queue',
            'statistics': 'statistics_queue'
        }
        
        queue = queue_map[worker_type]
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting Celery worker for {worker_type} queue...')
        )
        
        cmd = [
            'celery', '-A', 'CVProject', 'worker',
            '--loglevel', loglevel,
            '--concurrency', str(concurrency),
            '--queues', queue
        ]
        
        self.run_command(cmd)

    def run_command(self, cmd):
        """Run the Celery command."""
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'Error running Celery worker: {e}')
            )
            sys.exit(1)
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('Celery worker stopped by user')
            )


