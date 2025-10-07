"""
Management command to run various tasks manually.
"""
from django.core.management.base import BaseCommand, CommandError
from celery_tasks.tasks import *


class Command(BaseCommand):
    help = 'Run various Celery tasks manually'

    def add_arguments(self, parser):
        parser.add_argument(
            'task_name',
            type=str,
            help='Name of the task to run'
        )
        parser.add_argument(
            '--args',
            nargs='*',
            help='Arguments to pass to the task'
        )
        parser.add_argument(
            '--async',
            action='store_true',
            help='Run task asynchronously (queue it)'
        )

    def handle(self, *args, **options):
        task_name = options['task_name']
        task_args = options.get('args', [])
        run_async = options.get('async', False)

        # Map of available tasks
        available_tasks = {
            'generate_cv_pdf': generate_cv_pdf_task,
            'email_cv_pdf': email_cv_pdf_task,
            'analyze_cv': analyze_cv_task,
            'send_notification': send_notification_email,
            'send_cv_created_notification': send_cv_created_notification,
            'send_cv_updated_notification': send_cv_updated_notification,
            'cleanup_old_logs': cleanup_old_logs,
            'cleanup_old_pdf_files': cleanup_old_pdf_files,
            'cleanup_orphaned_files': cleanup_orphaned_files,
            'generate_daily_stats': generate_daily_stats,
            'generate_weekly_report': generate_weekly_report,
        }

        if task_name not in available_tasks:
            raise CommandError(f'Task "{task_name}" not found. Available tasks: {", ".join(available_tasks.keys())}')

        task_func = available_tasks[task_name]

        try:
            if run_async:
                # Run task asynchronously
                result = task_func.delay(*task_args)
                self.stdout.write(
                    self.style.SUCCESS(f'Task "{task_name}" queued with ID: {result.id}')
                )
            else:
                # Run task synchronously
                result = task_func(*task_args)
                self.stdout.write(
                    self.style.SUCCESS(f'Task "{task_name}" completed successfully. Result: {result}')
                )
        except Exception as e:
            raise CommandError(f'Task "{task_name}" failed: {str(e)}')
