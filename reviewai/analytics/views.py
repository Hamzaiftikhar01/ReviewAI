from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Count
from collections import Counter

from businesses.decorators import business_required
from reviews.models import Review, ReviewAnalysis
from ai import services as ai_services

@login_required
@business_required
def analytics_view(request):
    business = request.user.business
    now = timezone.now()
    
    # 1. Date Period Selection
    period = request.GET.get('period', '30d')
    
    if period == '7d':
        start_date = now - timezone.timedelta(days=7)
        steps = 7
        step_delta = timezone.timedelta(days=1)
        date_format = '%a'
    elif period == '90d':
        start_date = now - timezone.timedelta(days=90)
        steps = 12
        step_delta = timezone.timedelta(days=7)
        date_format = 'Wk %U'
    elif period == 'all':
        # Default all-time view but limits trend chart to last 120 days
        start_date = None
        steps = 12
        step_delta = timezone.timedelta(days=10)
        date_format = '%b %d'
    else: # 30d (default)
        start_date = now - timezone.timedelta(days=30)
        steps = 15
        step_delta = timezone.timedelta(days=2)
        date_format = '%b %d'
        
    # 2. Filter reviews
    reviews = Review.objects.filter(business=business)
    if start_date:
        reviews = reviews.filter(created_at__gte=start_date)
        
    total_reviews = reviews.count()
    
    # Sentiment Breakdown
    sentiment_counts = reviews.values('sentiment').annotate(count=Count('id'))
    sentiments = {s['sentiment']: s['count'] for s in sentiment_counts}
    
    pos_count = sentiments.get('Positive', 0)
    neg_count = sentiments.get('Negative', 0)
    neu_count = sentiments.get('Neutral', 0)
    
    analyzed_count = pos_count + neg_count + neu_count
    if analyzed_count > 0:
        pos_pct = round((pos_count / analyzed_count) * 100)
        neg_pct = round((neg_count / analyzed_count) * 100)
        neu_pct = round((neu_count / analyzed_count) * 100)
    else:
        pos_pct = neg_pct = neu_pct = 0

    # Rating Breakdown
    avg_rating_data = reviews.aggregate(Avg('rating'))
    avg_rating = round(avg_rating_data['rating__avg'] or 0.0, 1)
    
    distribution = {}
    for stars in range(5, 0, -1):
        count = reviews.filter(rating=stars).count()
        pct = round((count / total_reviews) * 100) if total_reviews > 0 else 0
        distribution[stars] = {'count': count, 'pct': pct}

    # 3. Dynamic Charts Generation (Trends over Selected Period)
    chart_labels = []
    total_volume_data = []
    positive_volume_data = []
    negative_volume_data = []
    
    for i in range(steps - 1, -1, -1):
        step_end = now - (i * step_delta)
        step_start = step_end - step_delta
        
        # Add labels
        chart_labels.append(step_end.strftime(date_format))
        
        # Query interval count
        interval_reviews = Review.objects.filter(
            business=business, 
            created_at__gte=step_start, 
            created_at__lt=step_end
        )
        total_volume_data.append(interval_reviews.count())
        positive_volume_data.append(interval_reviews.filter(sentiment='Positive').count())
        negative_volume_data.append(interval_reviews.filter(sentiment='Negative').count())

    # 4. Sources Distribution
    sources_data = reviews.values('source').annotate(count=Count('id'))
    sources = [{'source': s['source'], 'count': s['count']} for s in sources_data]

    # 5. Top Praise and Complaint topics
    analyses = ReviewAnalysis.objects.filter(review__business=business)
    if start_date:
        analyses = analyses.filter(review__created_at__gte=start_date)
        
    all_issues = []
    all_positives = []
    all_topics = []
    for a in analyses:
        all_issues.extend(a.issues)
        all_positives.extend(a.positive_aspects)
        all_topics.extend(a.topics)
        
    top_issues = [{'name': item[0], 'count': item[1]} for item in Counter(all_issues).most_common(5)]
    top_praises = [{'name': item[0], 'count': item[1]} for item in Counter(all_positives).most_common(5)]
    top_topics = [{'name': item[0], 'count': item[1]} for item in Counter(all_topics).most_common(5)]

    context = {
        'period': period,
        'total_reviews': total_reviews,
        'pos_count': pos_count,
        'neg_count': neg_count,
        'neu_count': neu_count,
        'pos_pct': pos_pct,
        'neg_pct': neg_pct,
        'neu_pct': neu_pct,
        'avg_rating': avg_rating,
        'distribution': distribution,
        'chart_labels': chart_labels,
        'total_volume_data': total_volume_data,
        'positive_volume_data': positive_volume_data,
        'negative_volume_data': negative_volume_data,
        'sources': sources,
        'top_issues': top_issues,
        'top_praises': top_praises,
        'top_topics': top_topics,
    }
    return render(request, 'analytics/index.html', context)


@login_required
@business_required
def ai_insights_view(request):
    business = request.user.business
    reviews = Review.objects.filter(business=business).order_by('-created_at')[:30]
    
    if reviews.count() < 3:
        context = {
            'insufficient_data': True,
            'reviews_count': reviews.count()
        }
        return render(request, 'analytics/ai_insights.html', context)
        
    # Check if insights are already generated in session
    insights = request.session.get('ai_insights_data', None)
    
    # If POST (regenerate request) or no insights in session
    if request.method == 'POST' or not insights:
        try:
            # Call AI service (failsafe mock is built-in)
            insights = ai_services.generate_aggregated_insights(business.name, reviews)
            request.session['ai_insights_data'] = insights
            messages.success(request, "AI Business Insights updated successfully!")
        except Exception as e:
            messages.error(request, f"Failed to generate insights: {str(e)}")
            insights = None
            
    context = {
        'insufficient_data': False,
        'insights': insights,
        'reviews_count': reviews.count()
    }
    return render(request, 'analytics/ai_insights.html', context)
