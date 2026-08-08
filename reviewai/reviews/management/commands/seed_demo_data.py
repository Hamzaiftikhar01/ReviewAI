import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from businesses.models import Business
from reviews.models import Review, ReviewAnalysis, AIReply
import ai.services as ai_services

class Command(BaseCommand):
    help = "Seed database with 3 diverse businesses and 40 reviews each (total 120 reviews) and trigger AI analysis."

    def handle(self, *args, **options):
        User = get_user_model()
        self.stdout.write("Starting database seeding process...")

        # Business configurations
        businesses_data = [
            {
                "email": "novacart@reviewai.com",
                "full_name": "NovaCart Administrator",
                "business_name": "NovaCart",
                "category": "E-commerce",
                "description": "Premium online retail marketplace specializing in electronics, apparel, and home essentials.",
                "location": "Global / Online",
                "website": "https://www.novacart-retail.com",
                "tone": "Casual",
                "reviews": [
                    ("Emily Johnson", 5, "The smartwatch is excellent. Battery lasts for days, highly visible outdoors, and steps tracking is accurate."),
                    ("Michael Smith", 5, "Fast delivery. Package arrived in perfect condition. Product works exactly as described."),
                    ("Sarah Davis", 3, "Ordered a red shirt but received a blue one. Support quickly refunded me, but order accuracy is poor."),
                    ("James Wilson", 1, "The shipping took over 3 weeks. Very disappointed with how slow the delivery was."),
                    ("Jessica Taylor", 1, "Customer support is nonexistent. Emailed them twice about my order status and got no response."),
                    ("David Brown", 4, "Good product quality for the price. Not high-end but definitely worth it."),
                    ("Robert Jones", 1, "The charging cable stopped working after 3 days. Extremely cheap quality."),
                    ("Linda Miller", 5, "Easy checkout experience on the website. Fast shipping and the item is great."),
                    ("William Garcia", 2, "Refund process is very complicated. They keep asking for photos of the damaged box."),
                    ("Karen Martinez", 3, "The package arrived wet due to rain. The item inside was protected, but packaging needs improvement."),
                    ("Richard Rodriguez", 5, "Great store with a wide range of products. I always buy my tech accessories here."),
                    ("Thomas Wilson", 3, "Average headphones. Sound is fine, but the ear cups are uncomfortable for long hours."),
                    ("Charles Thomas", 5, "Very fast shipping! Got my camera lens within 24 hours of placing the order."),
                    ("Christopher Moore", 1, "Item received is completely different from the website photos. Extremely misleading description."),
                    ("Daniel Jackson", 2, "Cheap materials. The plastic stand broke on day one. Returning it today."),
                    ("Matthew Martin", 5, "Amazing keyboard! The mechanical keys feel great and typing is very satisfying."),
                    ("Patricia Lee", 5, "The seller was very helpful when I needed to change my shipping address."),
                    ("Elizabeth Perez", 3, "Price is quite high compared to other online stores, but the shipping was fast."),
                    ("Jennifer Thompson", 2, "The phone screen arrived cracked. The packaging was too thin for fragile glass."),
                    ("Susan Harris", 5, "Great customer service. They solved my refund query within minutes."),
                    ("Joseph Clark", 3, "Average watch. Looks good but the step counter is way off."),
                    ("Thomas Lewis", 5, "Extremely fast shipping, product works as expected. Highly recommend!"),
                    ("Nancy Robinson", 2, "I ordered two lamps, only one arrived. Support told me the other is out of stock."),
                    ("Sandra Walker", 5, "Excellent customer support! They sent a replacement immediately when I reported a defect."),
                    ("Paul Young", 3, "Decent phone case. It protects the phone well but the color has already started fading."),
                    ("Mark Allen", 2, "The shipping was delayed by a week with no notification. Bad communication."),
                    ("Donald King", 2, "The package was left out in the rain by the delivery driver. Terrible packaging protection."),
                    ("George Wright", 5, "This wireless charger works perfectly. Very convenient and fast charging."),
                    ("Kenneth Scott", 1, "Terrible website experience. The checkout page kept crashing when I tried to pay."),
                    ("Steven Green", 5, "Super fast delivery. Got the product in under two days. Quality is great too."),
                    ("Edward Baker", 5, "The price of this tablet is unbeatable. Very happy with my purchase."),
                    ("Brian Adams", 1, "The support agent was rude and closed my chat before resolving my shipping issue."),
                    ("Ronald Nelson", 3, "Average vacuum cleaner. Decent suction but battery dies in 15 minutes."),
                    ("Timothy Carter", 5, "Product quality is very premium. Premium packaging and quick delivery."),
                    ("Jason Mitchell", 2, "The return shipping cost was not covered. I had to pay to send back a defective item."),
                    ("Jeffrey Perez", 5, "Very happy with the prompt response from customer support. Highly professional."),
                    ("Ryan Roberts", 4, "Shipping took slightly longer than expected, but the shoes are comfortable."),
                    ("Gary Turner", 2, "Incorrect item shipped. I received a small shirt instead of a medium size."),
                    ("Nicholas Phillips", 5, "Excellent laptop bag. Sturdy zippers and water-resistant fabric."),
                    ("Eric Campbell", 1, "The checkout page had a bug that charged me twice. Took a week to get my refund.")
                ]
            },
            {
                "email": "urbanbite@reviewai.com",
                "full_name": "UrbanBite Operations",
                "business_name": "UrbanBite",
                "category": "Restaurant",
                "description": "High-volume city center bistro specializing in local cuisines and rapid online delivery orders.",
                "location": "Downtown Food Court",
                "website": "https://www.urbanbite-bistro.com",
                "tone": "Warm",
                "reviews": [
                    ("Alex Carter", 5, "The gourmet burger was juicy and full of flavor. The fries were hot and crispy. 10/10!"),
                    ("Maria Bennett", 5, "Delivery was extremely fast! Food arrived hot and fresh in under twenty minutes."),
                    ("John Peterson", 2, "The pizza crust was burnt and the cheese was cold. Very disappointed with the quality today."),
                    ("Sophia Vance", 3, "Tasty pasta, but the portion size was way too small for what they charge."),
                    ("Liam Gallagher", 1, "Waited over an hour for our delivery. Food was cold when it finally arrived."),
                    ("Olivia Thorne", 5, "The staff at the counter were super friendly and welcoming. Great service."),
                    ("Jackson Reed", 1, "The delivery driver was rude and threw the bag on the porch. Food was messy inside."),
                    ("Chloe Jenkins", 5, "Beautiful dine-in experience. Great atmosphere, excellent service, and delicious steak."),
                    ("Ethan Hunt", 2, "They forgot to include the soft drinks we paid for. Order accuracy is terrible."),
                    ("Emma Stone", 2, "The packaging was crushed and the sauce leaked all over the bag. A total mess."),
                    ("Lucas Vance", 5, "Delicious sushi! Fresh fish and perfectly seasoned rice. Will definitely order again."),
                    ("Mia Hamm", 3, "Dine-in was fine, but the restaurant was extremely loud and tables were crowded."),
                    ("Noah Webster", 5, "Super fast food delivery! The burger was warm and tasty."),
                    ("Ava DuVernay", 1, "The chicken was dry and tasteless. Definitely not ordering the grilled chicken again."),
                    ("Oliver Twist", 4, "The menu prices are a bit high, but the quality of food justifies it."),
                    ("Sophia Loren", 5, "Amazing chocolate dessert! Rich flavor and beautiful presentation."),
                    ("Jack Nicholson", 2, "The waiter took 20 minutes just to bring water. Very slow table service."),
                    ("Isabella Rossellini", 5, "Good family restaurant. The kids loved the pizza and the staff were very accommodating."),
                    ("Daniel Day", 2, "The delivery was delayed. When I called the store, they said the driver just left."),
                    ("Grace Kelly", 5, "Amazing customer service. They quickly refunded our order when we reported a mix-up."),
                    ("Henry Cavill", 3, "Average noodles. Tastes okay but nothing special. Clean packaging."),
                    ("Zendaya Coleman", 5, "Highly recommend the garlic bread and lasagne. Absolutely authentic taste!"),
                    ("Tom Holland", 2, "The tacos were soggy because of the poor packaging. Needs ventilated boxes."),
                    ("Gigi Hadid", 3, "Fast delivery, but the food portion was very small for a main course."),
                    ("Bradley Cooper", 5, "Excellent service and cozy atmosphere. The soup was outstanding."),
                    ("Lady Gaga", 1, "The food arrived 40 minutes late and was completely stone cold."),
                    ("Billie Eilish", 4, "Staff was very polite. The food was fresh, although a bit under-seasoned."),
                    ("Justin Bieber", 2, "They delivered a vegetarian pizza instead of the pepperoni pizza I ordered."),
                    ("Selena Gomez", 5, "Super delicious chicken wings! The spicy sauce was perfect."),
                    ("Taylor Swift", 1, "Terrible service. The manager refused to replace a cold meal."),
                    ("Ed Sheeran", 4, "Decent meal. Price is reasonable, food quality is consistent."),
                    ("Dua Lipa", 1, "The restaurant hygiene was poor. Tables were sticky and floors were dirty."),
                    ("Shawn Mendes", 5, "Excellent delivery experience. Food was sealed perfectly and arrived hot."),
                    ("Camila Cabello", 3, "Average burger. The patty was a bit dry, but the sauce made it edible."),
                    ("Ariana Grande", 5, "The portion of salad was huge! Fresh ingredients and delicious dressing."),
                    ("Post Malone", 2, "Waited too long for dine-in seating even though we had a reservation."),
                    ("Drake Graham", 5, "Tasty wraps. Packaging was neat and delivery was right on time."),
                    ("Kendrick Lamar", 2, "The meal was overpriced for the simple ingredients. Not worth it."),
                    ("J Cole", 5, "Incredibly friendly delivery driver. Food was fresh and hot."),
                    ("Travis Scott", 2, "The soup was missing from our meal. Order accuracy needs improvement.")
                ]
            },
            {
                "email": "staysphere@reviewai.com",
                "full_name": "StaySphere Desk Manager",
                "business_name": "StaySphere",
                "category": "Hotel",
                "description": "Boutique resort hotel network offering lodging, premium amenities, and excursion management services.",
                "location": "Coastal Boulevard",
                "website": "https://www.staysphere-resort.com",
                "tone": "Formal",
                "reviews": [
                    ("Arthur Pendragon", 5, "The room was spotless and very modern. The king-size bed was exceptionally comfortable."),
                    ("Guinevere LeFay", 5, "The reception staff were incredibly friendly. They allowed us to check in early."),
                    ("Lancelot DuLac", 2, "The room was dusty and the bathroom was not cleaned properly. Disappointed."),
                    ("Merlin Ambrosius", 3, "Great location right in the center of the city. Wi-Fi was extremely slow though."),
                    ("Gawain Orkney", 2, "Terrible noise from the street. The room had poor sound insulation."),
                    ("Percival Wales", 5, "Beautiful hotel with great amenities. The rooftop pool and gym were excellent."),
                    ("Tristan Lyonesse", 5, "The breakfast buffet was outstanding! Lots of hot and cold options."),
                    ("Galahad Pure", 2, "The AC in our room stopped working at night. Front desk was slow to send help."),
                    ("Kay Seneschal", 5, "Excellent customer service. They quickly changed our room when we requested a quieter one."),
                    ("Bors Gannes", 2, "The room was very small and cramped. Not worth the high price we paid."),
                    ("Lamorak Gales", 5, "Spotless room and clean linens. Housekeeping did a wonderful job daily."),
                    ("Hector Maris", 3, "Decent hotel. Good location, but the check-in process took way too long."),
                    ("Bedivere Lucas", 5, "Lovely stay. The staff was very attentive and the breakfast was delicious."),
                    ("Gaheris Orkney", 1, "The Wi-Fi was down for our entire three-day stay. Very frustrating for work."),
                    ("Gareth Orkney", 4, "Great value for money. Simple rooms but clean and close to public transit."),
                    ("Dagonet Fool", 5, "Super check-out experience. Extremely fast and staff was very polite."),
                    ("Yvain Lion", 2, "The pool water was dirty and there were no clean towels available."),
                    ("Palamedes Saracen", 5, "Perfect family vacation spot. Kids enjoyed the play area and the breakfast was great."),
                    ("Erec Filia", 2, "The room smelled like smoke even though we booked a non-smoking room."),
                    ("Geraint Devon", 5, "Amazing customer service. They helped us book all our tours and transport."),
                    ("Balin Savage", 3, "Average hotel. Room was clean but the decor was very outdated."),
                    ("Balan Savage", 5, "Outstanding hospitality! The manager personally checked on us during breakfast."),
                    ("Pelleas Isles", 1, "The elevator was broken and we had to carry our heavy bags up four flights."),
                    ("Mordred Cornwall", 5, "Great location near all major sights, room was clean and cozy."),
                    ("Uther Pendragon", 3, "Decent stay. The room was fine, but the pricing is quite high for basic amenities."),
                    ("Igraine Cornwall", 2, "The bathroom plumbing was clogged. Took three hours for maintenance to fix."),
                    ("Gorlois Cornwall", 4, "Staff was very polite. Clean rooms, although the breakfast menu was repetitive."),
                    ("Elaine Astolat", 1, "They charged us twice for the stay. Had to spend hours resolving it with billing."),
                    ("Morgan Fey", 5, "Excellent gym and spa. Highly recommend booking a suite here."),
                    ("Nimue Lake", 1, "No hot water in the shower in the morning. Front desk just said they are working on it."),
                    ("Joseph Arimathea", 5, "Perfect room quality. The bed was plush and the view was gorgeous."),
                    ("Galahad Galahad", 2, "The room was next to the service elevator and was extremely noisy all night."),
                    ("Percival Knight", 5, "Clean hotel, helpful staff. Walking distance to the beach."),
                    ("Tristan Knight", 2, "Average breakfast. The coffee was cold and pastries were stale."),
                    ("Yvain Knight", 5, "Amazing stay! The room was clean, spacious, and the location was quiet."),
                    ("Lancelot Knight", 2, "Housekeeping forgot to change our towels for two days."),
                    ("Gawain Knight", 5, "Friendly reception. Very easy checkout. Will definitely return."),
                    ("Kay Knight", 2, "The room rate is overpriced. Gym is tiny and only has two treadmills."),
                    ("Bors Knight", 5, "Excellent customer care. They prepared a packed breakfast for our early flight."),
                    ("Bedivere Knight", 1, "The room door lock was broken. We felt unsafe and had to demand a room change.")
                ]
            }
        ]

        for b_data in businesses_data:
            self.stdout.write(f"Configuring owner user: {b_data['email']}...")
            user, created = User.objects.get_or_create(
                email=b_data["email"],
                defaults={
                    "full_name": b_data["full_name"],
                    "is_active": True
                }
            )
            if created or not user.check_password("password123"):
                user.set_password("password123")
                user.save()

            self.stdout.write(f"Creating business profile: {b_data['business_name']}...")
            business, b_created = Business.objects.update_or_create(
                owner=user,
                defaults={
                    "name": b_data["business_name"],
                    "category": b_data["category"],
                    "description": b_data["description"],
                    "location": b_data["location"],
                    "website": b_data["website"],
                    "tone": b_data["tone"]
                }
            )

            # Clear existing reviews to ensure clean state
            Review.objects.filter(business=business).delete()

            self.stdout.write(f"Generating 40 reviews for {b_data['business_name']}...")
            now = timezone.now()
            
            for index, (cust_name, rating, text) in enumerate(b_data["reviews"]):
                # Spread dates over the last 30 days
                days_offset = random.randint(0, 30)
                hours_offset = random.randint(0, 23)
                minutes_offset = random.randint(0, 59)
                created_date = now - timedelta(days=days_offset, hours=hours_offset, minutes=minutes_offset)

                review = Review.objects.create(
                    business=business,
                    customer_name=cust_name,
                    customer_email=f"{cust_name.lower().replace(' ', '')}@example.com",
                    rating=rating,
                    review_text=text,
                    source=random.choice(["Google", "Manual", "CSV Import"]),
                    sentiment="Pending",
                    status="Unanalyzed"
                )
                
                # Override auto-now created_at for historical reporting accuracy
                Review.objects.filter(id=review.id).update(created_at=created_date)
                review.refresh_from_db()

                # Process AI Heuristics/Sentiment Analysis
                analysis_result = ai_services.analyze_review(review.review_text, review.rating)
                
                ReviewAnalysis.objects.create(
                    review=review,
                    sentiment=analysis_result["sentiment"],
                    confidence=analysis_result["confidence"],
                    issues=analysis_result["issues"],
                    positive_aspects=analysis_result["positive_aspects"],
                    topics=analysis_result["topics"],
                    summary=analysis_result["summary"]
                )

                # Set review status to analyzed
                review.sentiment = analysis_result["sentiment"]
                review.status = "Analyzed"
                review.save()

                # Generate and save AI reply suggestion
                reply_text = ai_services.generate_local_mock_reply(
                    business_name=business.name,
                    tone=business.tone,
                    customer_name=review.customer_name,
                    rating=review.rating,
                    sentiment=review.sentiment,
                    positives=analysis_result["positive_aspects"],
                    issues=analysis_result["issues"]
                )
                
                AIReply.objects.create(
                    review=review,
                    reply_text=reply_text,
                    is_saved=False
                )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully with 120 AI-analyzed reviews across E-Commerce, Restaurants, and Hotels!"))
