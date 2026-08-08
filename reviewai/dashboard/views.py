from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Avg, Count
from collections import Counter

from businesses.decorators import business_required
from reviews.models import Review, ReviewAnalysis, AIReply

@login_required
@business_required
def dashboard_view(request):
    business = request.user.business
    now = timezone.now()
    
    # 1. Basic Stats Calculations
    total_reviews = Review.objects.filter(business=business).count()
    
    sentiment_counts = Review.objects.filter(business=business).values('sentiment').annotate(count=Count('id'))
    sentiments = {s['sentiment']: s['count'] for s in sentiment_counts}
    
    pos_count = sentiments.get('Positive', 0)
    neg_count = sentiments.get('Negative', 0)
    neu_count = sentiments.get('Neutral', 0)
    pen_count = sentiments.get('Pending', 0)
    
    # Percentages
    analyzed_count = pos_count + neg_count + neu_count
    if analyzed_count > 0:
        pos_pct = round((pos_count / analyzed_count) * 100)
        neg_pct = round((neg_count / analyzed_count) * 100)
        neu_pct = round((neu_count / analyzed_count) * 100)
    else:
        pos_pct = neg_pct = neu_pct = 0
        
    avg_rating_data = Review.objects.filter(business=business).aggregate(Avg('rating'))
    avg_rating = round(avg_rating_data['rating__avg'] or 0.0, 1)

    # 2. Dynamic Trend Indicators
    # Compare last 30 days reviews count to previous 30 days reviews count
    last_30_days_start = now - timezone.timedelta(days=30)
    prev_30_days_start = now - timezone.timedelta(days=60)
    
    current_period_count = Review.objects.filter(
        business=business, 
        created_at__gte=last_30_days_start
    ).count()
    
    prev_period_count = Review.objects.filter(
        business=business, 
        created_at__gte=prev_30_days_start, 
        created_at__lt=last_30_days_start
    ).count()
    
    if prev_period_count > 0:
        reviews_trend = round(((current_period_count - prev_period_count) / prev_period_count) * 100)
    else:
        reviews_trend = None

    # Rating trend
    current_rating_avg = Review.objects.filter(
        business=business, 
        created_at__gte=last_30_days_start
    ).aggregate(Avg('rating'))['rating__avg']
    
    prev_rating_avg = Review.objects.filter(
        business=business, 
        created_at__gte=prev_30_days_start, 
        created_at__lt=last_30_days_start
    ).aggregate(Avg('rating'))['rating__avg']
    
    if current_rating_avg and prev_rating_avg:
        rating_trend = round(current_rating_avg - prev_rating_avg, 2)
    else:
        rating_trend = None

    # 3. Rating Distribution
    distribution = {}
    for stars in range(5, 0, -1):
        count = Review.objects.filter(business=business, rating=stars).count()
        pct = round((count / total_reviews) * 100) if total_reviews > 0 else 0
        distribution[stars] = {'count': count, 'pct': pct}

    # 4. Chart Data (Volume over last 7 days)
    chart_labels = []
    chart_data = []
    for i in range(6, -1, -1):
        date = (now - timezone.timedelta(days=i)).date()
        chart_labels.append(date.strftime('%b %d'))
        count = Review.objects.filter(business=business, created_at__date=date).count()
        chart_data.append(count)

    # 5. Recent Reviews (Last 5)
    recent_reviews = Review.objects.filter(business=business).order_by('-created_at')[:5]

    # 6. Top Issues (Aggregated from ReviewAnalysis JSON fields)
    analyses = ReviewAnalysis.objects.filter(review__business=business)
    issues_list = []
    for analysis in analyses:
        issues_list.extend(analysis.issues)
    
    # Count occurrences
    issues_counter = Counter(issues_list)
    top_issues = [{'issue': item[0], 'count': item[1]} for item in issues_counter.most_common(3)]

    # 7. AI Reply Preview (Latest saved AI reply)
    recent_reply = AIReply.objects.filter(
        review__business=business, 
        is_saved=True
    ).order_by('-updated_at').first()

    context = {
        'total_reviews': total_reviews,
        'pos_count': pos_count,
        'neg_count': neg_count,
        'neu_count': neu_count,
        'pen_count': pen_count,
        'pos_pct': pos_pct,
        'neg_pct': neg_pct,
        'neu_pct': neu_pct,
        'avg_rating': avg_rating,
        'reviews_trend': reviews_trend,
        'rating_trend': rating_trend,
        'distribution': distribution,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'recent_reviews': recent_reviews,
        'top_issues': top_issues,
        'recent_reply': recent_reply,
        'business': business
    }
    return render(request, 'dashboard/index.html', context)
