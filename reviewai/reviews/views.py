import csv
import io
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.utils import timezone

from businesses.decorators import business_required
from .models import Review, ReviewAnalysis, AIReply
from .forms import ReviewManualForm, CSVImportForm
from ai import services as ai_services
from notifications.models import Notification

@login_required
@business_required
def reviews_list(request):
    business = request.user.business
    queryset = Review.objects.filter(business=business)

    # Search query
    search_query = request.GET.get('search', '').strip()
    if search_query:
        queryset = queryset.filter(
            Q(customer_name__icontains=search_query) |
            Q(review_text__icontains=search_query)
        )

    # Filters
    sentiment_filter = request.GET.get('sentiment', '')
    if sentiment_filter:
        queryset = queryset.filter(sentiment=sentiment_filter)

    rating_filter = request.GET.get('rating', '')
    if rating_filter:
        queryset = queryset.filter(rating=rating_filter)

    source_filter = request.GET.get('source', '')
    if source_filter:
        queryset = queryset.filter(source=source_filter)

    # Date filter
    date_filter = request.GET.get('date_range', '')
    if date_filter == '7d':
        start_date = timezone.now() - timezone.timedelta(days=7)
        queryset = queryset.filter(created_at__gte=start_date)
    elif date_filter == '30d':
        start_date = timezone.now() - timezone.timedelta(days=30)
        queryset = queryset.filter(created_at__gte=start_date)
    elif date_filter == '90d':
        start_date = timezone.now() - timezone.timedelta(days=90)
        queryset = queryset.filter(created_at__gte=start_date)

    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    valid_sorts = ['created_at', '-created_at', 'rating', '-rating']
    if sort_by in valid_sorts:
        queryset = queryset.order_by(sort_by)

    # Pagination
    paginator = Paginator(queryset, 10)  # 10 reviews per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Count stats
    total_reviews = Review.objects.filter(business=business).count()

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'sentiment_filter': sentiment_filter,
        'rating_filter': rating_filter,
        'source_filter': source_filter,
        'date_filter': date_filter,
        'sort_by': sort_by,
        'total_reviews': total_reviews,
    }
    return render(request, 'reviews/list.html', context)


@login_required
@business_required
def review_detail(request, pk):
    business = request.user.business
    review = get_object_or_404(Review, id=pk, business=business)
    
    # Check if analysis or reply exists
    analysis = getattr(review, 'analysis', None)
    ai_reply = getattr(review, 'ai_reply', None)

    context = {
        'review': review,
        'analysis': analysis,
        'ai_reply': ai_reply,
        'tones': [t[0] for t in business.TONE_CHOICES]
    }
    return render(request, 'reviews/detail.html', context)


@login_required
@business_required
def review_create(request):
    if request.method == 'POST':
        form = ReviewManualForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.business = request.user.business
            review.save()
            messages.success(request, f"Review for {review.customer_name} added successfully!")
            return redirect('review_detail', pk=review.id)
    else:
        form = ReviewManualForm()
        
    return render(request, 'reviews/create.html', {'form': form})


@login_required
@business_required
@require_POST
def review_analyze_ai(request, pk):
    business = request.user.business
    review = get_object_or_404(Review, id=pk, business=business)
    
    try:
        # Run AI analysis (falls back to local rules if API not active)
        analysis_result = ai_services.analyze_review(review.review_text, review.rating)
        
        # Save or update Analysis
        analysis, created = ReviewAnalysis.objects.update_or_create(
            review=review,
            defaults={
                'sentiment': analysis_result['sentiment'],
                'confidence': analysis_result['confidence'],
                'issues': analysis_result['issues'],
                'positive_aspects': analysis_result['positive_aspects'],
                'topics': analysis_result['topics'],
                'summary': analysis_result['summary'],
            }
        )
        
        # Update original Review cache fields
        review.sentiment = analysis_result['sentiment']
        review.status = 'Analyzed'
        review.save()

        # Trigger notification if sentiment is negative
        if review.sentiment == 'Negative':
            Notification.objects.create(
                user=request.user,
                message=f"Negative review alert: {review.customer_name} left a {review.rating}★ review.",
                notification_type='negative_review'
            )
        else:
            Notification.objects.create(
                user=request.user,
                message=f"AI sentiment analysis completed for {review.customer_name}'s review.",
                notification_type='ai_analysis'
            )

        messages.success(request, "AI sentiment analysis completed successfully!")
    except Exception as e:
        messages.error(request, f"AI analysis failed: {str(e)}")
        
    return redirect('review_detail', pk=review.id)


@login_required
@business_required
@require_POST
def review_generate_reply_ai(request, pk):
    business = request.user.business
    review = get_object_or_404(Review, id=pk, business=business)
    
    # Check if analysis exists. If not, analyze first
    if review.status != 'Analyzed' or not hasattr(review, 'analysis'):
        messages.warning(request, "Analyzing review before generating a reply...")
        # Inline analyze
        analysis_result = ai_services.analyze_review(review.review_text, review.rating)
        ReviewAnalysis.objects.update_or_create(
            review=review,
            defaults={
                'sentiment': analysis_result['sentiment'],
                'confidence': analysis_result['confidence'],
                'issues': analysis_result['issues'],
                'positive_aspects': analysis_result['positive_aspects'],
                'topics': analysis_result['topics'],
                'summary': analysis_result['summary'],
            }
        )
        review.sentiment = analysis_result['sentiment']
        review.status = 'Analyzed'
        review.save()
        
    analysis = review.analysis
    selected_tone = request.POST.get('tone', business.tone)
    
    try:
        reply_text = ai_services.generate_reply(
            business_name=business.name,
            tone=selected_tone,
            customer_name=review.customer_name,
            rating=review.rating,
            sentiment=review.sentiment,
            positives=analysis.positive_aspects,
            issues=analysis.issues,
            review_text=review.review_text
        )
        
        # Save or update AIReply
        AIReply.objects.update_or_create(
            review=review,
            defaults={
                'reply_text': reply_text,
                'is_saved': False
            }
        )
        messages.success(request, f"AI suggested response generated with a {selected_tone} tone!")
    except Exception as e:
        messages.error(request, f"Failed to generate reply: {str(e)}")
        
    return redirect('review_detail', pk=review.id)


@login_required
@business_required
@require_POST
def review_save_reply(request, pk):
    business = request.user.business
    review = get_object_or_404(Review, id=pk, business=business)
    ai_reply = get_object_or_404(AIReply, review=review)
    
    reply_text = request.POST.get('reply_text', '').strip()
    if not reply_text:
        messages.error(request, "Reply text cannot be empty.")
        return redirect('review_detail', pk=review.id)
        
    ai_reply.reply_text = reply_text
    ai_reply.is_saved = True
    ai_reply.save()
    
    messages.success(request, "AI Suggested reply updated and saved successfully!")
    return redirect('review_detail', pk=review.id)


@login_required
@business_required
@require_POST
def review_delete(request, pk):
    business = request.user.business
    review = get_object_or_404(Review, id=pk, business=business)
    review.delete()
    messages.success(request, "Review deleted successfully.")
    return redirect('reviews_list')


# --- CSV IMPORT VIEWS ---

@login_required
@business_required
def csv_import_upload(request):
    if request.method == 'POST':
        form = CSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            
            # Read CSV data
            try:
                decoded_file = csv_file.read().decode('utf-8')
                io_string = io.StringIO(decoded_file)
                reader = csv.reader(io_string)
                
                # Check header
                header = [h.strip().lower() for h in next(reader, [])]
                required_cols = ['customer_name', 'rating', 'review_text']
                missing_cols = [col for col in required_cols if col not in header]
                
                if missing_cols:
                    messages.error(request, f"Invalid CSV format. Missing required columns: {', '.join(missing_cols)}")
                    return render(request, 'reviews/csv_upload.html', {'form': form})
                
                # Column indices
                name_idx = header.index('customer_name')
                rating_idx = header.index('rating')
                text_idx = header.index('review_text')
                
                email_idx = header.index('customer_email') if 'customer_email' in header else -1
                source_idx = header.index('source') if 'source' in header else -1
                
                valid_rows = []
                errors = []
                row_num = 1  # 1-indexed count after header
                
                for row in reader:
                    row_num += 1
                    if not row or all(cell == '' for cell in row):
                        continue
                    
                    # Read values
                    c_name = row[name_idx].strip() if name_idx < len(row) else ''
                    c_rating_raw = row[rating_idx].strip() if rating_idx < len(row) else ''
                    c_text = row[text_idx].strip() if text_idx < len(row) else ''
                    
                    c_email = row[email_idx].strip() if (email_idx != -1 and email_idx < len(row)) else ''
                    c_source = row[source_idx].strip() if (source_idx != -1 and source_idx < len(row)) else 'CSV Import'
                    
                    # Basic row validation
                    row_errors = []
                    if not c_name:
                        row_errors.append("Customer name is required.")
                    
                    if not c_text:
                        row_errors.append("Review text is required.")
                        
                    rating_val = None
                    try:
                        rating_val = int(c_rating_raw)
                        if rating_val < 1 or rating_val > 5:
                            row_errors.append(f"Rating '{rating_val}' must be between 1 and 5.")
                    except ValueError:
                        row_errors.append(f"Rating '{c_rating_raw}' must be a valid integer.")
                        
                    if row_errors:
                        errors.append(f"Row {row_num}: " + " | ".join(row_errors))
                    else:
                        valid_rows.append({
                            'customer_name': c_name,
                            'customer_email': c_email,
                            'rating': rating_val,
                            'review_text': c_text,
                            'source': c_source or 'CSV Import'
                        })
                
                # Save preview data to session
                request.session['csv_import_data'] = valid_rows
                
                context = {
                    'form': form,
                    'valid_rows': valid_rows,
                    'errors': errors,
                    'total_valid': len(valid_rows),
                    'total_errors': len(errors)
                }
                return render(request, 'reviews/csv_preview.html', context)
                
            except Exception as e:
                messages.error(request, f"Error processing CSV file: {str(e)}")
    else:
        form = CSVImportForm()
        
    return render(request, 'reviews/csv_upload.html', {'form': form})


@login_required
@business_required
@require_POST
def csv_import_confirm(request):
    import_data = request.session.get('csv_import_data', [])
    if not import_data:
        messages.error(request, "No import preview data found in session.")
        return redirect('csv_upload')
        
    business = request.user.business
    created_count = 0
    
    for row in import_data:
        Review.objects.create(
            business=business,
            customer_name=row['customer_name'],
            customer_email=row['customer_email'] or None,
            rating=row['rating'],
            review_text=row['review_text'],
            source=row['source'],
            sentiment='Pending',
            status='Unanalyzed'
        )
        created_count += 1
        
    # Clear session data
    if 'csv_import_data' in request.session:
        del request.session['csv_import_data']
        
    # Create notification
    Notification.objects.create(
        user=request.user,
        message=f"CSV import completed successfully. {created_count} reviews imported.",
        notification_type='csv_import'
    )
    
    messages.success(request, f"Successfully imported {created_count} reviews!")
    return redirect('reviews_list')
