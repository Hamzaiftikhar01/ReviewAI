import json
import os
import requests
import logging
from django.conf import settings
from . import prompts

logger = logging.getLogger(__name__)

def is_api_configured():
    """Check if the Gemini API key is configured in environment variables."""
    return bool(os.getenv("GEMINI_API_KEY"))

def call_gemini_api(prompt, response_json=False):
    """Make a direct HTTP request to the Gemini API."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is missing.")

    # Using gemini-1.5-flash as it is fast and supports JSON response format
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    
    if response_json:
        payload["generationConfig"] = {
            "responseMimeType": "application/json"
        }
        
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=12)
        response.raise_for_status()
        result = response.json()
        
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        return text
    except Exception as e:
        logger.error(f"Gemini API request failed: {e}")
        raise e

# --- LOCAL MOCK FALLBACK SYSTEM ---

def run_local_mock_analysis(review_text, rating):
    """Analyze review sentiment and extract issues/positives locally as a fallback."""
    text_lower = review_text.lower()
    
    # Heuristics for sentiment based on rating and keywords
    positive_words = ["good", "great", "excellent", "love", "amazing", "delicious", "friendly", "perfect", "happy", "best", "clean"]
    negative_words = ["bad", "late", "slow", "worst", "rude", "poor", "expensive", "dirty", "cold", "waste", "disappointed", "delay"]
    
    pos_count = sum(1 for w in positive_words if w in text_lower)
    neg_count = sum(1 for w in negative_words if w in text_lower)
    
    # Sentiment calculation
    if rating >= 4:
        sentiment = "Positive"
        confidence = 0.85 + (pos_count * 0.02)
    elif rating <= 2:
        sentiment = "Negative"
        confidence = 0.85 + (neg_count * 0.02)
    else:
        if neg_count > pos_count:
            sentiment = "Negative"
        elif pos_count > neg_count:
            sentiment = "Positive"
        else:
            sentiment = "Neutral"
        confidence = 0.70
        
    confidence = min(0.99, confidence)
    
    # Extract topics & issues
    issues = []
    positives = []
    topics = []
    
    if "delivery" in text_lower or "driver" in text_lower or "late" in text_lower:
        topics.append("delivery")
        if "late" in text_lower or "slow" in text_lower:
            issues.append("Late delivery")
        elif "good" in text_lower or "fast" in text_lower:
            positives.append("Fast delivery")
            
    if "food" in text_lower or "taste" in text_lower or "delicious" in text_lower or "eat" in text_lower:
        topics.append("food")
        if "cold" in text_lower or "bad" in text_lower or "tasteless" in text_lower:
            issues.append("Food quality issues")
        else:
            positives.append("Food quality")
            
    if "service" in text_lower or "staff" in text_lower or "waiter" in text_lower or "manager" in text_lower or "rude" in text_lower:
        topics.append("service")
        if "rude" in text_lower or "slow" in text_lower:
            issues.append("Staff behavior")
        else:
            positives.append("Friendly service")
            
    if "price" in text_lower or "expensive" in text_lower or "cost" in text_lower or "cheap" in text_lower:
        topics.append("pricing")
        if "expensive" in text_lower or "overpriced" in text_lower:
            issues.append("High pricing")
        else:
            positives.append("Good value")
            
    # Default tags if nothing matched
    if not topics:
        topics = ["general"]
    if sentiment == "Positive" and not positives:
        positives = ["Overall experience"]
    if sentiment == "Negative" and not issues:
        issues = ["General service standard"]
        
    summary = f"Customer expressed a {sentiment.lower()} opinion with {rating}-star rating."
    if positives:
        summary += f" Appreciated: {', '.join(positives)}."
    if issues:
        summary += f" Complaints: {', '.join(issues)}."
        
    return {
        "sentiment": sentiment,
        "confidence": confidence,
        "issues": issues,
        "positive_aspects": positives,
        "topics": topics,
        "summary": summary
    }

def generate_local_mock_reply(business_name, tone, customer_name, rating, sentiment, positives, issues):
    """Generate review response locally as a fallback using templates styled by business tone."""
    # Handle lists
    pos_str = ", ".join(positives) if positives else "our service"
    issue_str = ", ".join(issues) if issues else "any issues"
    
    if sentiment == "Positive":
        if tone == "Casual":
            return f"Hey {customer_name}! Thanks a lot for the {rating}-star review! We're thrilled you loved our {pos_str}. See you again soon!"
        elif tone == "Warm":
            return f"Dear {customer_name}, thank you so much for your kind words! We are absolutely delighted that you enjoyed your experience and our {pos_str}. Warmest regards!"
        elif tone == "Formal":
            return f"Dear {customer_name}, thank you for taking the time to share your feedback. We appreciate your commendation regarding our {pos_str} and are glad to have met your expectations."
        else: # Professional
            return f"Thank you for the review, {customer_name}. We appreciate your positive feedback regarding the {pos_str} and look forward to serving you again."
            
    elif sentiment == "Negative":
        if tone == "Casual":
            return f"Hi {customer_name}, really sorry to hear that things didn't go well, especially regarding the {issue_str}. We are on it and hope to make it up to you next time!"
        elif tone == "Warm":
            return f"Dear {customer_name}, we are so sorry you had a disappointing experience. We take complaints about {issue_str} very seriously and are working with our staff to resolve this. We hope to welcome you back soon."
        elif tone == "Formal":
            return f"Dear {customer_name}, please accept our sincere apologies for the issues encountered. We have documented your concerns regarding {issue_str} and are conducting an internal review to address these shortfalls."
        else: # Professional
            return f"We apologize for the inconvenience, {customer_name}. We take your feedback regarding {issue_str} seriously and are taking active measures to improve our operational standards."
            
    else: # Neutral
        return f"Thank you for your feedback, {customer_name}. We appreciate your honest review and will keep your notes about {issue_str} and {pos_str} in mind as we continue to refine our service."

# --- PUBLIC SERVICE API METHODS ---

def analyze_review(review_text, rating):
    """
    Analyzes a review using Gemini AI. Falls back to a local rules-based analyzer
    if GEMINI_API_KEY is missing or if the API call fails.
    """
    if is_api_configured():
        try:
            prompt = prompts.SENTIMENT_ANALYSIS_PROMPT.format(review_text=review_text)
            response_text = call_gemini_api(prompt, response_json=True)
            data = json.loads(response_text)
            
            # Map API lowercase sentiment to title case model sentiment
            raw_sentiment = data.get("sentiment", "neutral").lower()
            sentiment_map = {"positive": "Positive", "negative": "Negative", "neutral": "Neutral"}
            
            return {
                "sentiment": sentiment_map.get(raw_sentiment, "Neutral"),
                "confidence": float(data.get("confidence", 0.90)),
                "issues": data.get("issues", []),
                "positive_aspects": data.get("positive_aspects", []),
                "topics": data.get("topics", []),
                "summary": data.get("summary", "Review analyzed successfully.")
            }
        except Exception as e:
            logger.warning(f"Error calling Gemini API for analysis, falling back to local analysis: {e}")
            
    # Local Fallback
    return run_local_mock_analysis(review_text, rating)

def generate_reply(business_name, tone, customer_name, rating, sentiment, positives, issues, review_text):
    """
    Generates a reply suggestion using Gemini AI. Falls back to a local templates engine
    if GEMINI_API_KEY is missing or if the API call fails.
    """
    if is_api_configured():
        try:
            prompt = prompts.REPLY_GENERATION_PROMPT.format(
                business_name=business_name,
                customer_name=customer_name,
                rating=rating,
                sentiment=sentiment,
                review_text=review_text,
                positives=", ".join(positives) if positives else "none",
                issues=", ".join(issues) if issues else "none",
                tone=tone
            )
            reply = call_gemini_api(prompt, response_json=False)
            return reply.strip().strip('"') # Clean trailing quotes
        except Exception as e:
            logger.warning(f"Error calling Gemini API for reply generation, falling back to local: {e}")

    # Local Fallback
    return generate_local_mock_reply(business_name, tone, customer_name, rating, sentiment, positives, issues)

def generate_aggregated_insights(business_name, reviews):
    """
    Aggregates reviews and calls Gemini AI to get structured trends.
    If API is offline, generates standard mock recommendations based on DB counts.
    """
    # Prepare reviews data for prompt
    review_summaries = []
    negative_count = 0
    total_rating = 0
    issue_counts = {}
    praised_counts = {}
    
    for r in reviews:
        total_rating += r.rating
        if r.sentiment == 'Negative':
            negative_count += 1
            # Tally issues if analysis exists
            if hasattr(r, 'analysis'):
                for issue in r.analysis.issues:
                    issue_counts[issue] = issue_counts.get(issue, 0) + 1
        elif r.sentiment == 'Positive':
            if hasattr(r, 'analysis'):
                for pos in r.analysis.positive_aspects:
                    praised_counts[pos] = praised_counts.get(pos, 0) + 1
                    
        review_summaries.append(f"- [{r.rating} stars] ({r.sentiment}): \"{r.review_text}\"")

    reviews_str = "\n".join(review_summaries[:30]) # Limit to last 30 reviews to stay within context
    
    # Sort issues and praises
    sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
    sorted_praises = sorted(praised_counts.items(), key=lambda x: x[1], reverse=True)
    
    top_issues = [f"{item[0]} ({item[1]} mentions)" for item in sorted_issues[:3]]
    top_praises = [f"{item[0]} ({item[1]} mentions)" for item in sorted_praises[:3]]
    
    if len(reviews) < 3:
        return {
            "overall_sentiment_summary": "Not enough review data to generate a reliable insight.",
            "biggest_complaints": [],
            "most_praised_features": [],
            "emerging_issues": "None detected due to limited sample size.",
            "recommendations": []
        }
        
    if is_api_configured():
        try:
            prompt = prompts.AGGREGATED_INSIGHTS_PROMPT.format(
                business_name=business_name,
                reviews_data=reviews_str
            )
            response_text = call_gemini_api(prompt, response_json=True)
            return json.loads(response_text)
        except Exception as e:
            logger.warning(f"Error calling Gemini API for aggregated insights, falling back to local: {e}")
            
    # Local Fallback Insights based on ORM statistics
    avg_rating = round(total_rating / len(reviews), 1)
    neg_pct = round((negative_count / len(reviews)) * 100)
    
    summary = f"Based on {len(reviews)} reviews, {business_name} maintains a rating of {avg_rating}/5. "
    if neg_pct > 25:
        summary += f"Action is required as negative reviews make up {neg_pct}% of total feedback."
    else:
        summary += f"Customer sentiment is largely positive, with only {neg_pct}% negative reviews."
        
    mock_recommendations = []
    if top_issues:
        clean_issue = sorted_issues[0][0].lower()
        mock_recommendations.append(f"Direct operational focus toward resolving '{clean_issue}', which is your leading complaint.")
    else:
        mock_recommendations.append("Continue tracking feedback and encourage customers to detail their visits.")
        
    if top_praises:
        clean_praise = sorted_praises[0][0].lower()
        mock_recommendations.append(f"Leverage '{clean_praise}' in your marketing copy as it is highly valued by customers.")
    else:
        mock_recommendations.append("Develop a core service highlight to build promotional campaigns around.")
        
    mock_recommendations.append("Establish a standard process to reply to all negative reviews within 24 hours to improve retention.")
    
    return {
        "overall_sentiment_summary": summary,
        "biggest_complaints": top_issues if top_issues else ["General delivery speed", "Staff response times"],
        "most_praised_features": top_praises if top_praises else ["Product selection", "Customer satisfaction"],
        "emerging_issues": f"Minor concerns regarding {sorted_issues[0][0].lower()} if volume increases." if top_issues else "No new emerging complaints identified.",
        "recommendations": mock_recommendations
    }
