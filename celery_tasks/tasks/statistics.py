"""
Statistics and reporting tasks.
"""
from datetime import datetime, timedelta
from typing import Dict, Any
from celery import shared_task
from django.utils import timezone
from django.db.models import Count, Q

from main.models import CV, RequestLog


@shared_task(bind=True, name='celery_tasks.tasks.statistics.generate_daily_stats')
def generate_daily_stats(self, date=None) -> Dict[str, Any]:
    """
    Generate daily statistics.
    
    Args:
        date: Date to generate stats for (defaults to yesterday)
        
    Returns:
        Dict with daily statistics
    """
    try:
        if date is None:
            date = timezone.now().date() - timedelta(days=1)
        
        # Get date range
        start_date = timezone.make_aware(datetime.combine(date, datetime.min.time()))
        end_date = start_date + timedelta(days=1)
        
        # Count CVs created on this date
        cvs_created = CV.objects.filter(
            created_at__gte=start_date,
            created_at__lt=end_date
        ).count()
        
        # Count requests on this date
        requests_count = RequestLog.objects.filter(
            timestamp__gte=start_date,
            timestamp__lt=end_date
        ).count()
        
        # Count unique users
        unique_users = RequestLog.objects.filter(
            timestamp__gte=start_date,
            timestamp__lt=end_date
        ).values('user').distinct().count()
        
        # Most popular CVs (by request count)
        popular_cvs = CV.objects.annotate(
            request_count=Count('requestlog', filter=Q(
                requestlog__timestamp__gte=start_date,
                requestlog__timestamp__lt=end_date
            ))
        ).filter(request_count__gt=0).order_by('-request_count')[:5]
        
        stats = {
            'date': date.isoformat(),
            'cvs_created': cvs_created,
            'requests_count': requests_count,
            'unique_users': unique_users,
            'popular_cvs': [
                {
                    'id': cv.id,
                    'name': f'{cv.firstname} {cv.lastname}',
                    'request_count': cv.request_count
                }
                for cv in popular_cvs
            ]
        }
        
        return {
            'status': 'success',
            'stats': stats,
            'message': f'Daily stats generated for {date}'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task(bind=True, name='celery_tasks.tasks.statistics.generate_weekly_report')
def generate_weekly_report(self, week_start=None) -> Dict[str, Any]:
    """
    Generate weekly statistics report.
    
    Args:
        week_start: Start date of the week (defaults to last Monday)
        
    Returns:
        Dict with weekly statistics
    """
    try:
        if week_start is None:
            today = timezone.now().date()
            days_since_monday = today.weekday()
            week_start = today - timedelta(days=days_since_monday)
        
        # Get week range
        start_date = timezone.make_aware(datetime.combine(week_start, datetime.min.time()))
        end_date = start_date + timedelta(days=7)
        
        # Count CVs created this week
        cvs_created = CV.objects.filter(
            created_at__gte=start_date,
            created_at__lt=end_date
        ).count()
        
        # Count total requests this week
        requests_count = RequestLog.objects.filter(
            timestamp__gte=start_date,
            timestamp__lt=end_date
        ).count()
        
        # Count unique users this week
        unique_users = RequestLog.objects.filter(
            timestamp__gte=start_date,
            timestamp__lt=end_date
        ).values('user').distinct().count()
        
        # Daily breakdown
        daily_stats = []
        for i in range(7):
            day_date = week_start + timedelta(days=i)
            day_start = timezone.make_aware(datetime.combine(day_date, datetime.min.time()))
            day_end = day_start + timedelta(days=1)
            
            day_requests = RequestLog.objects.filter(
                timestamp__gte=day_start,
                timestamp__lt=day_end
            ).count()
            
            daily_stats.append({
                'date': day_date.isoformat(),
                'requests': day_requests
            })
        
        # Most active CVs this week
        active_cvs = CV.objects.annotate(
            request_count=Count('requestlog', filter=Q(
                requestlog__timestamp__gte=start_date,
                requestlog__timestamp__lt=end_date
            ))
        ).filter(request_count__gt=0).order_by('-request_count')[:10]
        
        report = {
            'week_start': week_start.isoformat(),
            'week_end': (week_start + timedelta(days=6)).isoformat(),
            'cvs_created': cvs_created,
            'total_requests': requests_count,
            'unique_users': unique_users,
            'daily_stats': daily_stats,
            'active_cvs': [
                {
                    'id': cv.id,
                    'name': f'{cv.firstname} {cv.lastname}',
                    'request_count': cv.request_count
                }
                for cv in active_cvs
            ]
        }
        
        return {
            'status': 'success',
            'report': report,
            'message': f'Weekly report generated for week starting {week_start}'
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }
