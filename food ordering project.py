
from flask import Flask, request, render_template_string, jsonify
import mysql.connector as sql
from datetime import datetime, timedelta
import random
import string

app = Flask(__name__)

# Mock database configuration (Unused in this demo, but kept for context)
DB_CONFIG = {
    'host': "localhost",
    'user': "root",
    'password': "@prince",
    'database': "food"
}

# In-memory demo storage
otp_store = {}
cart = {}
logged_in_user = None
order_history = {}
order_status_progression = ['Order Placed', 'Preparing', 'Out for Delivery', 'Delivered']

def db_cursor():
    """Establishes a connection to the database and returns the connection and cursor."""
    mydb = sql.connect(**DB_CONFIG)
    return mydb, mydb.cursor()

# List of unique background images for different pages
background_images = [
    'https://images.unsplash.com/photo-1544025162-d76694265947?q=80&w=1800&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1542838139-4824707172c3?q=80&w=1800&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1540321288344-f8b8a5b28d54?q=80&w=1800&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1518843875463-c774431536b6?q=80&w=1800&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1506368249639-73a05d6f642e?q=80&w=1800&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1550547660-d9450f859349?q=80&w=1800&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1579737190530-589578297b6a?q=80&w=1800&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1563245366-0714b10223e7?q=80&w=1800&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1595086812836-8a58e45371c6?q=80&w=1800&auto=format&fit=crop',
    'https://images.unsplash.com/photo-1517729226508-b78f45a0b77b?q=80&w=1800&auto=format&fit=crop'
]

# The complete list of all food items with tags and other data
food_items_full = [
    {'id': 1, 'name': 'Behrouz Biryani', 'tags': 'Biryani • Mughlai', 'rating': 4.4, 'time': 32, 'price': 299, 'img': 'https://images.unsplash.com/photo-1505935428862-770b6f24f629?q=80&w=800&auto=format&fit=crop', 'quality': 'Smoky and flavorful, slow-cooked to perfection.'},
    {'id': 2, 'name': 'Burger King', 'tags': 'Burgers • Fast Food', 'rating': 4.2, 'time': 28, 'price': 199, 'img': 'https://images.unsplash.com/photo-1550547660-d9450f859349?q=80&w=800&auto=format&fit=crop', 'quality': 'Flame-grilled burgers with fresh veggies.'},
    {'id': 3, 'name': 'La Pizzetta', 'tags': 'Italian • Pizza', 'rating': 4.5, 'time': 35, 'price': 399, 'img': 'https://images.unsplash.com/photo-1548365328-9f547fb0953e?q=80&w=800&auto=format&fit=crop', 'quality': 'Authentic Italian pizza with a crispy thin crust.'},
    {'id': 4, 'name': 'The Curry Leaf', 'tags': 'North Indian • Thali', 'rating': 4.3, 'time': 30, 'price': 199, 'img': 'https://images.unsplash.com/photo-1604908177010-0f9b578d5a1?q=80&w=800&auto=format&fit=crop', 'quality': 'Homestyle North Indian curries and fresh bread.'},
    {'id': 5, 'name': 'Dimsum House', 'tags': 'Chinese • Asian', 'rating': 4.1, 'time': 27, 'price': 99, 'img': 'https://images.unsplash.com/photo-1553621042-f6e147245754?q=80&w=800&auto=format&fit=crop', 'quality': 'Steamed and fried dimsums with a variety of fillings.'},
    {'id': 6, 'name': 'Sugar & Spoon', 'tags': 'Desserts • Bakery', 'rating': 4.7, 'time': 25, 'price': 199, 'img': 'https://images.unsplash.com/photo-1511920170033-f8396924c348?q=80&w=800&auto=format&fit=crop', 'quality': 'Decadent chocolate pastries and cakes.'},
    {'id': 7, 'name': 'McDonalds', 'tags': 'Burgers • Fast Food', 'rating': 4.0, 'time': 22, 'price': 499, 'img': 'https://images.unsplash.com/photo-1565299624946-b28f40a1740a?q=80&w=800&auto=format&fit=crop', 'quality': 'Classic American burgers and fries.'},
    {'id': 8, 'name': 'Haldirams', 'tags': 'Sweets • Snacks', 'rating': 4.6, 'time': 24, 'price': 49, 'img': 'https://images.unsplash.com/photo-1627915354504-2d57b2b8d009?q=80&w=800&auto=format&fit=crop', 'quality': 'Authentic Indian sweets and savory snacks.'},
    {'id': 9, 'name': 'Pizza Hut', 'tags': 'Pizza • Italian', 'rating': 4.5, 'time': 20, 'price': 120, 'img': 'https://images.unsplash.com/photo-1579737190530-589578297b6a?q=80&w=800&auto=format&fit=crop', 'quality': 'Pan pizzas with a variety of toppings.'},
    {'id': 10, 'name': 'Dominos', 'tags': 'Pizza • Fast Food', 'rating': 4.8, 'time': 25, 'price': 150, 'img': 'https://images.unsplash.com/photo-1604313620601-52f01f07b71f?q=80&w=800&auto=format&fit=crop', 'quality': 'Cheesy pizzas delivered hot and fast.'},
    {'id': 11, 'name': 'The Wok Shop', 'tags': 'Chinese • Noodles', 'rating': 4.3, 'time': 35, 'price': 250, 'img': 'https://images.unsplash.com/photo-1563245366-0714b10223e7?q=80&w=800&auto=format&fit=crop', 'quality': 'Stir-fried noodles and rice from the wok.'},
    {'id': 12, 'name': 'Kebab King', 'tags': 'Mughlai • Tandoori', 'rating': 4.6, 'time': 40, 'price': 450, 'img': 'https://images.unsplash.com/photo-1599307849646-7c98c0b2f567?q=80&w=800&auto=format&fit=crop', 'quality': 'Juicy kebabs and tandoori delights.'},
    {'id': 13, 'name': 'Chaats & More', 'tags': 'Street Food • Indian', 'rating': 4.1, 'time': 20, 'price': 80, 'img': 'https://images.unsplash.com/photo-1627915354504-2d57b2b8d009?q=80&w=800&auto=format&fit=crop', 'quality': 'Spicy and tangy street food favorites.'},
    {'id': 14, 'name': 'Coffee House', 'tags': 'Beverages • Snacks', 'rating': 4.7, 'time': 15, 'price': 100, 'img': 'https://images.unsplash.com/photo-1595183353597-285b73d61a29?q=80&w=800&auto=format&fit=crop', 'quality': 'Artisan coffee and light snacks.'},
    {'id': 15, 'name': 'Hyderabadi House', 'tags': 'Biryani • South Indian', 'rating': 4.7, 'time': 38, 'price': 350, 'img': 'https://images.unsplash.com/photo-1631557990595-364426466f27?q=80&w=800&auto=format&fit=crop', 'quality': 'Aromatic Hyderabadi-style biryani.'},
    {'id': 16, 'name': 'Subway', 'tags': 'Salads • Sandwiches', 'rating': 4.3, 'time': 18, 'price': 250, 'img': 'https://images.unsplash.com/photo-1621516135069-07f9c2d7681c?q=80&w=800&auto=format&fit=crop', 'quality': 'Fresh and customizable sandwiches and salads.'},
    {'id': 17, 'name': 'Taco Bell', 'tags': 'Mexican • Fast Food', 'rating': 4.0, 'time': 25, 'price': 220, 'img': 'https://images.unsplash.com/photo-1626201386705-1a8684725d2b?q=80&w=800&auto=format&fit=crop', 'quality': 'Crunchy tacos and cheesy nachos.'},
    {'id': 18, 'name': 'KFC', 'tags': 'Fried Chicken • Fast Food', 'rating': 4.2, 'time': 28, 'price': 300, 'img': 'https://images.unsplash.com/photo-1574631388656-1d1e434f3c7d?q=80&w=800&auto=format&fit=crop', 'quality': 'Crispy and juicy fried chicken.'},
    {'id': 19, 'name': 'Paan Factory', 'tags': 'Desserts • Paan', 'rating': 4.9, 'time': 15, 'price': 70, 'img': 'https://images.unsplash.com/photo-1563245366-0714b10223e7?q=80&w=800&auto=format&fit=crop', 'quality': 'Sweet and refreshing paan varieties.'},
    {'id': 20, 'name': 'Wow! Momo', 'tags': 'Street Food • Asian', 'rating': 4.8, 'time': 20, 'price': 180, 'img': 'https://images.unsplash.com/photo-1627915354504-2d57b2b8d009?q=80&w=800&auto=format&fit=crop', 'quality': 'Steamed momos with hot and spicy dips.'},
    {'id': 21, 'name': 'Starbucks', 'tags': 'Beverages • Coffee', 'rating': 4.5, 'time': 10, 'price': 250, 'img': 'https://images.unsplash.com/photo-1521017430489-082b99214d18?q=80&w=800&auto=format&fit=crop', 'quality': 'Premium coffee and comfortable cafe experience.'},
    {'id': 22, 'name': 'Cafe Coffee Day', 'tags': 'Beverages • Snacks', 'rating': 4.1, 'time': 15, 'price': 150, 'img': 'https://images.unsplash.com/photo-1517729226508-b78f45a0b77b?q=80&w=800&auto=format&fit=crop', 'quality': 'Affordable coffee and quick snacks.'},
    {'id': 23, 'name': 'Biryani Blues', 'tags': 'Biryani • North Indian', 'rating': 4.6, 'time': 35, 'price': 320, 'img': 'https://images.unsplash.com/photo-1569058145719-75f11a877a5b?q=80&w=800&auto=format&fit=crop', 'quality': 'Classic biryani with a rich, blue-spiced flavor.'},
    {'id': 24, 'name': 'Bombay Sweets', 'tags': 'Sweets • Indian', 'rating': 4.9, 'time': 20, 'price': 60, 'img': 'https://images.unsplash.com/photo-1627915354504-2d57b2b8d009?q=80&w=800&auto=format&fit=crop', 'quality': 'Authentic Mumbai-style sweets.'},
    {'id': 25, 'name': 'Thali Express', 'tags': 'Thali • Indian', 'rating': 4.4, 'time': 30, 'price': 280, 'img': 'https://images.unsplash.com/photo-1563729573883-294c7b8c7e0c?q=80&w=800&auto=format&fit=crop', 'quality': 'A complete meal with multiple dishes.'},
    {'id': 26, 'name': 'South Indian Dosa', 'tags': 'South Indian • Dosa', 'rating': 4.7, 'time': 25, 'price': 180, 'img': 'https://images.unsplash.com/photo-1595086812836-8a58e45371c6?q=80&w=800&auto=format&fit=crop', 'quality': 'Crispy dosas with a variety of chutneys.'},
    {'id': 27, 'name': 'Dunkin Donuts', 'tags': 'Desserts • Bakery', 'rating': 4.1, 'time': 15, 'price': 100, 'img': 'https://images.unsplash.com/photo-1579737190530-589578297b6a?q=80&w=800&auto=format&fit=crop', 'quality': 'Sweet and savory donuts.'},
    {'id': 28, 'name': 'Baskin Robbins', 'tags': 'Desserts • Ice Cream', 'rating': 4.6, 'time': 15, 'price': 150, 'img': 'https://images.unsplash.com/photo-1517729226508-b78f45a0b77b?q=80&w=800&auto=format&fit=crop', 'quality': 'Rich and creamy ice cream flavors.'},
    {'id': 29, 'name': 'Mughlai Darbar', 'tags': 'Mughlai • Curry', 'rating': 4.5, 'time': 45, 'price': 400, 'img': 'https://images.unsplash.com/photo-1604908177010-0f9b578d5a1?q=80&w=800&auto=format&fit=crop', 'quality': 'Traditional Mughlai curries with rich gravies.'},
    {'id': 30, 'name': 'Chinese Wok', 'tags': 'Chinese • Asian', 'rating': 4.3, 'time': 30, 'price': 220, 'img': 'https://images.unsplash.com/photo-1563245366-0714b10223e7?q=80&w=800&auto=format&fit=crop', 'quality': 'Classic Chinese wok dishes.'},
    {'id': 31, 'name': 'Grill House', 'tags': 'Grill • Fast Food', 'rating': 4.4, 'time': 25, 'price': 280, 'img': 'https://images.unsplash.com/photo-1599307849646-7c98c0b2f567?q=80&w=800&auto=format&fit=crop', 'quality': 'Grilled meats and fresh vegetables.'},
    {'id': 32, 'name': 'Healthy Salads', 'tags': 'Salads • Bowls', 'rating': 4.8, 'time': 20, 'price': 300, 'img': 'https://images.unsplash.com/photo-1556139943-4bdca53adf1e?q=80&w=800&auto=format&fit=crop', 'quality': 'Fresh and organic salad bowls.'},
    {'id': 33, 'name': 'Chai Point', 'tags': 'Beverages • Indian', 'rating': 4.6, 'time': 15, 'price': 80, 'img': 'https://images.unsplash.com/photo-1616035091216-724d1a0e77d7?q=80&w=800&auto=format&fit=crop', 'quality': 'Traditional Indian tea and snacks.'},
    {'id': 34, 'name': 'Cold Stone Creamery', 'tags': 'Desserts • Ice Cream', 'rating': 4.7, 'time': 18, 'price': 200, 'img': 'https://images.unsplash.com/photo-1517729226508-b78f45a0b77b?q=80&w=800&auto=format&fit=crop', 'quality': 'Customized ice cream creations.'},
    {'id': 35, 'name': 'Wraps & Rolls', 'tags': 'Fast Food • Wraps', 'rating': 4.3, 'time': 25, 'price': 150, 'img': 'https://images.unsplash.com/photo-1621516135069-07f9c2d7681c?q=80&w=800&auto=format&fit=crop', 'quality': 'Variety of wraps and Kathi rolls.'},
    {'id': 36, 'name': 'Keventers', 'tags': 'Beverages • Milkshakes', 'rating': 4.9, 'time': 15, 'price': 180, 'img': 'https://images.unsplash.com/photo-1521017430489-082b99214d18?q=80&w=800&auto=format&fit=crop', 'quality': 'Thick and creamy milkshakes.'},
    {'id': 37, 'name': 'Theobroma', 'tags': 'Desserts • Brownies', 'rating': 4.8, 'time': 20, 'price': 120, 'img': 'https://images.unsplash.com/photo-1511920170033-f8396924c348?q=80&w=800&auto=format&fit=crop', 'quality': 'Rich and gooey brownies and desserts.'},
    {'id': 38, 'name': 'Chilli Chicken Express', 'tags': 'Chinese • Fast Food', 'rating': 4.2, 'time': 30, 'price': 280, 'img': 'https://images.unsplash.com/photo-1563245366-0714b10223e7?q=80&w=800&auto=format&fit=crop', 'quality': 'Spicy chicken dishes and Indo-Chinese food.'},
    {'id': 39, 'name': 'Punjabi Rasoi', 'tags': 'North Indian • Curry', 'rating': 4.5, 'time': 40, 'price': 350, 'img': 'https://images.unsplash.com/photo-1604908177010-0f9b578d5a1?q=80&w=800&auto=format&fit=crop', 'quality': 'Hearty Punjabi food with butter and spices.'},
    {'id': 40, 'name': 'Veggie Delight', 'tags': 'Salads • Healthy', 'rating': 4.7, 'time': 22, 'price': 250, 'img': 'https://images.unsplash.com/photo-1556139943-4bdca53adf1e?q=80&w=800&auto=format&fit=crop', 'quality': 'Fresh, vibrant, and healthy salads.'},
    {'id': 41, 'name': 'Cheesecake Factory', 'tags': 'Desserts • Cake', 'rating': 4.9, 'time': 25, 'price': 400, 'img': 'https://images.unsplash.com/photo-1511920170033-f8396924c348?q=80&w=800&auto=format&fit=crop', 'quality': 'Famous for its wide variety of cheesecakes.'},
    {'id': 42, 'name': 'Sagar Ratna', 'tags': 'South Indian • Dosa', 'rating': 4.4, 'time': 30, 'price': 200, 'img': 'https://images.unsplash.com/photo-1595086812836-8a58e45371c6?q=80&w=800&auto=format&fit=crop', 'quality': 'Authentic South Indian vegetarian food.'},
    {'id': 43, 'name': 'Biryani By Kilo', 'tags': 'Biryani • Mughlai', 'rating': 4.8, 'time': 45, 'price': 500, 'img': 'https://images.unsplash.com/photo-1505935428862-770b6f24f629?q=80&w=800&auto=format&fit=crop', 'quality': 'Biryani cooked in traditional earthen pots.'},
    {'id': 44, 'name': 'Fat Lulu\'s', 'tags': 'Pizza • Italian', 'rating': 4.6, 'time': 35, 'price': 450, 'img': 'https://images.unsplash.com/photo-1548365328-9f547fb0953e?q=80&w=800&auto=format&fit=crop', 'quality': 'Hand-tossed pizzas with gourmet ingredients.'},
    {'id': 45, 'name': 'The Belgian Waffle Co.', 'tags': 'Desserts • Waffles', 'rating': 4.7, 'time': 20, 'price': 150, 'img': 'https://images.unsplash.com/photo-1579737190530-589578297b6a?q=80&w=800&auto=format&fit=crop', 'quality': 'Hot, crispy waffles with rich toppings.'},
    {'id': 46, 'name': 'Chai Sutta Bar', 'tags': 'Beverages • Snacks', 'rating': 4.0, 'time': 15, 'price': 50, 'img': 'https://images.unsplash.com/photo-1616035091216-724d1a0e77d7?q=80&w=800&auto=format&fit=crop', 'quality': 'Casual spot for Indian tea and street snacks.'},
    {'id': 47, 'name': 'Insta Burger', 'tags': 'Burgers • Fast Food', 'rating': 4.3, 'time': 22, 'price': 200, 'img': 'https://images.unsplash.com/photo-1550547660-d9450f859349?q=80&w=800&auto=format&fit=crop', 'quality': 'Juicy beef and chicken burgers.'},
    {'id': 48, 'name': 'The Great Indian Thali', 'tags': 'Thali • Indian', 'rating': 4.5, 'time': 40, 'price': 350, 'img': 'https://images.unsplash.com/photo-1563729573883-294c7b8c7e0c?q=80&w=800&auto=format&fit=crop', 'quality': 'Unlimited thali with regional specialties.'},
    {'id': 49, 'name': 'Burrito Bowl Co.', 'tags': 'Mexican • Bowls', 'rating': 4.4, 'time': 25, 'price': 300, 'img': 'https://images.unsplash.com/photo-1626201386705-1a8684725d2b?q=80&w=800&auto=format&fit=crop', 'quality': 'Fresh and wholesome burrito bowls.'},
    {'id': 50, 'name': 'Pan-Asian Express', 'tags': 'Chinese • Asian', 'rating': 4.1, 'time': 30, 'price': 280, 'img': 'https://images.unsplash.com/photo-1563245366-0714b10223e7?q=80&w=800&auto=format&fit=crop', 'quality': 'Fast delivery of popular Asian dishes.'},
    {'id': 51, 'name': 'Nirula\'s', 'tags': 'Ice Cream • Fast Food', 'rating': 4.2, 'time': 20, 'price': 150, 'img': 'https://images.unsplash.com/photo-1517729226508-b78f45a0b77b?q=80&w=800&auto=format&fit=crop', 'quality': 'Classic ice creams and family-friendly food.'},
    {'id': 52, 'name': 'Jalebi Wala', 'tags': 'Sweets • Indian', 'rating': 4.8, 'time': 15, 'price': 50, 'img': 'https://images.unsplash.com/photo-1627915354504-2d57b2b8d009?q=80&w=800&auto=format&fit=crop', 'quality': 'Crispy jalebis fried to a golden perfection.'},
    {'id': 53, 'name': 'Dilli Chaat House', 'tags': 'Street Food • Indian', 'rating': 4.5, 'time': 18, 'price': 90, 'img': 'https://images.unsplash.com/photo-1627915354504-2d57b2b8d009?q=80&w=800&auto=format&fit=crop', 'quality': 'Authentic street-style chaat from Delhi.'},
    {'id': 54, 'name': 'Rolls King', 'tags': 'Wraps • Fast Food', 'rating': 4.3, 'time': 25, 'price': 180, 'img': 'https://images.unsplash.com/photo-1621516135069-07f9c2d7681c?q=80&w=800&auto=format&fit=crop', 'quality': 'Hearty and filling wraps and rolls.'},
    {'id': 55, 'name': 'Sardarji\'s Kitchen', 'tags': 'North Indian • Tandoori', 'rating': 4.7, 'time': 40, 'price': 400, 'img': 'https://images.unsplash.com/photo-1604908177010-0f9b578d5a1?q=80&w=800&auto=format&fit=crop', 'quality': 'Delicious tandoori items and rich curries.'},
    {'id': 56, 'name': 'The Italian Stallion', 'tags': 'Italian • Pasta', 'rating': 4.6, 'time': 30, 'price': 320, 'img': 'https://images.unsplash.com/photo-1548365328-9f547fb0953e?q=80&w=800&auto=format&fit=crop', 'quality': 'Freshly made pasta with creamy sauces.'},
    {'id': 57, 'name': 'Momos & More', 'tags': 'Asian • Momos', 'rating': 4.8, 'time': 20, 'price': 150, 'img': 'https://images.unsplash.com/photo-1627915354504-2d57b2b8d009?q=80&w=800&auto=format&fit=crop', 'quality': 'Steamed and pan-fried momos with spicy chutney.'},
    {'id': 58, 'name': 'Healthy Heart', 'tags': 'Healthy • Salads', 'rating': 4.9, 'time': 15, 'price': 280, 'img': 'https://images.unsplash.com/photo-1556139943-4bdca53adf1e?q=80&w=800&auto=format&fit=crop', 'quality': 'Nutritious and delicious meal bowls.'},
    {'id': 59, 'name': 'Amritsari Dhaba', 'tags': 'North Indian • Curry', 'rating': 4.4, 'time': 45, 'price': 380, 'img': 'https://images.unsplash.com/photo-1604908177010-0f9b578d5a1?q=80&w=800&auto=format&fit=crop', 'quality': 'Authentic Amritsari-style food with a buttery flavor.'},
    {'id': 60, 'name': 'Sweet Tooth', 'tags': 'Desserts • Sweets', 'rating': 4.7, 'time': 20, 'price': 100, 'img': 'https://images.unsplash.com/photo-1511920170033-f8396924c348?q=80&w=800&auto=format&fit=crop', 'quality': 'Classic Indian and western desserts.'},
    {'id': 61, 'name': 'Veggie Wok', 'tags': 'Chinese', 'rating': 4.2, 'time': 30, 'price': 210, 'img': 'https://images.unsplash.com/photo-1563245366-0714b10223e7?q=80&w=800&auto=format&fit=crop', 'quality': 'Flavorful vegetarian Chinese dishes.'},
    {'id': 62, 'name': 'Pizza Town', 'tags': 'Pizza', 'rating': 4.6, 'time': 28, 'price': 350, 'img': 'https://images.unsplash.com/photo-1548365328-9f547fb0953e?q=80&w=800&auto=format&fit=crop', 'quality': 'Freshly baked pizza with fresh toppings.'},
    {'id': 63, 'name': 'The Dosa Factory', 'tags': 'South Indian', 'rating': 4.5, 'time': 25, 'price': 150, 'img': 'https://images.unsplash.com/photo-1595086812836-8a58e45371c6?q=80&w=800&auto=format&fit=crop', 'quality': 'Wide range of dosas and South Indian delicacies.'},
    {'id': 64, 'name': 'Tandoori Tales', 'tags': 'North Indian', 'rating': 4.7, 'time': 40, 'price': 420, 'img': 'https://images.unsplash.com/photo-1604908177010-0f9b578d5a1?q=80&w=800&auto=format&fit=crop', 'quality': 'Rich and creamy North Indian food.'},
    {'id': 65, 'name': 'Cafe Mocha', 'tags': 'Coffee', 'rating': 4.8, 'time': 15, 'price': 180, 'img': 'https://images.unsplash.com/photo-1521017430489-082b99214d18?q=80&w=800&auto=format&fit=crop', 'quality': 'Smooth and aromatic coffee.'},
    {'id': 66, 'name': 'The Cake Stop', 'tags': 'Desserts', 'rating': 4.9, 'time': 20, 'price': 300, 'img': 'https://images.unsplash.com/photo-1511920170033-f8396924c348?q=80&w=800&auto=format&fit=crop', 'quality': 'Delicious cakes for all occasions.'},
    {'id': 67, 'name': 'Wrap It Up', 'tags': 'Wraps', 'rating': 4.3, 'time': 25, 'price': 160, 'img': 'https://images.unsplash.com/photo-1621516135069-07f9c2d7681c?q=80&w=800&auto=format&fit=crop', 'quality': 'Healthy wraps with a variety of fillings.'},
    {'id': 68, 'name': 'Bihari Foods', 'tags': 'Indian', 'rating': 4.0, 'time': 35, 'price': 250, 'img': 'https://images.unsplash.com/photo-1627915354504-2d57b2b8d009?q=80&w=800&auto=format&fit=crop', 'quality': 'Authentic Bihari cuisine.'},
    {'id': 69, 'name': 'The Juice Bar', 'tags': 'Beverages', 'rating': 4.6, 'time': 10, 'price': 120, 'img': 'https://images.unsplash.com/photo-1595183353597-285b73d61a29?q=80&w=800&auto=format&fit=crop', 'quality': 'Freshly squeezed juices.'},
    {'id': 70, 'name': 'Ice Cream Parlour', 'tags': 'Desserts • Ice Cream', 'rating': 4.7, 'time': 15, 'price': 180, 'img': 'https://images.unsplash.com/photo-1517729226508-b78f45a0b77b?q=80&w=800&auto=format&fit=crop', 'quality': 'Homemade ice cream flavors.'}
]

# The main HTML structure
base_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Swifty — Food & Groceries Delivered</title>
    <style>
        :root {
            --accent: #FC8019; --accent-2: #FD9139; --text: #1a1a1a; --muted: #666;
            --bg: #fffaf6; --card: #ffffff; --stroke: rgba(0, 0, 0, 0.08);
            --radius: 22px; --shadow: 0 8px 20px rgba(0, 0, 0, .08), 0 2px 8px rgba(0, 0, 0, .04);
            --dark-card: rgba(0,0,0,0.65);
        }
        * { box-sizing: border-box; }
        html, body { height: 100%; }
        body {
            margin: 0; font-family: "Inter", system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji";
            color: var(--text);
            line-height: 1.4;
            transition: background 0.5s ease;
        }
        body:not(.other-page) {
            background: radial-gradient(1200px 800px at 85% -10%, rgba(252, 128, 25, .08), transparent 60%), var(--bg);
        }
        body.other-page {
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #fff;
            min-height: 100vh;
        }
        .header { position: sticky; top: 0; z-index: 50; backdrop-filter: saturate(1.2) blur(8px); background: color-mix(in srgb, #fff 70%, transparent); border-bottom: 1px solid var(--stroke); }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        .nav { display: flex; align-items: center; justify-content: space-between; min-height: 72px; }
        .brand { display: flex; align-items: center; gap: 12px; font-weight: 800; font-size: 20px; letter-spacing: .2px; }
        .logo { width: 34px; height: 34px; border-radius: 10px; background: conic-gradient(from 20deg, var(--accent), var(--accent-2)); box-shadow: 0 6px 14px rgba(252, 128, 25, .3); }
        .nav-actions { display: flex; align-items: center; gap: 10px; }
        .btn { appearance: none; border: none; background: var(--text); color: #fff; padding: 12px 16px; border-radius: 14px; font-weight: 600; cursor: pointer; transition: transform .1s ease, box-shadow .2s ease; }
        .btn:active { transform: translateY(1px); }
        .btn.secondary { background: #fff; color: var(--text); border: 1px solid var(--stroke); }
        .pill { display: inline-flex; align-items: center; gap: 8px; padding: 9px 12px; border-radius: 999px; border: 1px solid var(--stroke); background: #fff; font-weight: 500; }
        .hero { padding: 40px 0 20px; position: relative; overflow: hidden; }
        .hero-grid { display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 30px; align-items: center; }
        .headline { font-size: 44px; line-height: 1.1; margin: 6px 0 14px; letter-spacing: -.5px; }
        .sub { color: var(--muted); max-width: 55ch; }
        .searchbar { display: flex; gap: 10px; margin-top: 18px; }
        .input { flex: 1; display: flex; align-items: center; gap: 10px; border: 1px solid var(--stroke); background: #fff; border-radius: 16px; padding: 12px 14px; }
        .input input { border: none; outline: none; font-size: 16px; width: 100%; background: transparent; }
        .cta { display: flex; gap: 10px; margin-top: 10px; }
        .float { position: absolute; filter: drop-shadow(0 10px 20px rgba(0, 0, 0, .12)); animation: float 6s ease-in-out infinite; }
        .float:nth-child(1) { top: 5%; right: -40px; animation-delay: .2s; }
        .float:nth-child(2) { bottom: 8%; right: 10%; animation-delay: 1s; }
        .float:nth-child(3) { top: 18%; right: 26%; animation-delay: 1.8s; }
        @keyframes float { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
        .chips { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 14px; }
        .chip { padding: 10px 12px; background: #fff; border: 1px solid var(--stroke); border-radius: 999px; font-weight: 600; }
        a { display: block; margin-top: 15px; text-align: center; color: #ffcc29; font-weight: bold; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .chips li { list-style: none; }
        .chips li a { text-decoration: none; display: inline-block; padding: 10px 20px; background: #ffcc29; color: #000; font-weight: bold; border-radius: 6px; transition: all 0.3s ease; }
        .chips li a:hover { background: #ff9900; color: #fff; }
        .scroller { margin-top: 26px; display: flex; gap: 14px; overflow: auto; padding-bottom: 6px; scroll-snap-type: x mandatory; }
        .scroller::-webkit-scrollbar { height: 8px; }
        .scroller::-webkit-scrollbar-thumb { background: rgba(0, 0, 0, .12); border-radius: 999px; }
        .cat { min-width: 160px; scroll-snap-align: start; background: linear-gradient(180deg, #fff, #fff8f0); border: 1px solid var(--stroke); border-radius: 18px; box-shadow: var(--shadow); padding: 14px; display: flex; align-items: center; gap: 12px; }
        .cat img { width: 52px; height: 52px; border-radius: 12px; object-fit: cover; }
        .cat b { font-size: 15px; }
        .section { padding: 24px 0 8px; }
        .section h2 { font-size: 26px; margin: 0 0 8px; }
        .section p { margin: 0; color: var(--muted); }
        .grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 16px 0 40px; }
        .card { position: relative; background: linear-gradient(180deg, #fff, #fffdf9); border: 1px solid var(--stroke); border-radius: 20px; box-shadow: var(--shadow); overflow: hidden; transition: transform .18s ease, box-shadow .2s ease; }
        .card:hover { transform: translateY(-3px); box-shadow: 0 16px 30px rgba(0, 0, 0, .12); }
        .ratio { position: relative; aspect-ratio: 4/3; background: linear-gradient(90deg, #eee 25%, #f7f7f7 37%, #eee 63%); background-size: 400% 100%; animation: shimmer 1.4s infinite; }
        @keyframes shimmer { 0% { background-position: 100% 0; } 100% { background-position: -100% 0; } }
        .ratio img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; opacity: 0; transition: opacity .5s ease; }
        .card .content { padding: 12px 14px 16px; }
        .title { font-weight: 700; }
        .muted { color: var(--muted); font-size: 14px; }
        .meta { display: flex; gap: 10px; align-items: center; margin-top: 8px; justify-content: space-between; }
        .badge { display: inline-flex; align-items: center; gap: 6px; padding: 6px 8px; border-radius: 10px; border: 1px solid var(--stroke); background: #fff; font-weight: 600; font-size: 13px; }
        .rating { background: linear-gradient(180deg, #22c55e, #16a34a); color: #fff; border: none; }
        .fav { position: absolute; top: 10px; right: 10px; width: 40px; height: 40px; border-radius: 12px; border: 1px solid var(--stroke); background: #fff; display: grid; place-items: center; font-size: 18px; cursor: pointer; box-shadow: var(--shadow); }
        .fav.active { background: var(--accent); color: #fff; }
        .offers { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
        .offer { border: 1px dashed rgba(252, 128, 25, .4); background: linear-gradient(90deg, rgba(252, 128, 25, .08), #fff); border-radius: 18px; padding: 16px 18px; font-weight: 700; }
        .cta-banner { margin: 34px 0; background: linear-gradient(45deg, var(--accent), var(--accent-2)); color: #fff; border-radius: 26px; padding: 26px 24px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 16px 40px rgba(252, 128, 25, .35); }
        .cta-banner b { font-size: 22px; }
        .store { display: flex; gap: 10px; }
        .store a { display: inline-flex; align-items: center; gap: 10px; background: #111; color: #fff; padding: 10px 14px; border-radius: 12px; text-decoration: none; font-weight: 700; }
        footer { margin: 40px 0 50px; border-top: 1px solid var(--stroke); }
        .footgrid { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 20px; padding-top: 24px; }
        footer a { color: inherit; text-decoration: none; }
        .toast { position: fixed; left: 50%; transform: translateX(-50%) translateY(20px); bottom: -80px; z-index: 100; background: #111; color: #fff; border-radius: 14px; padding: 12px 16px; font-weight: 700; box-shadow: 0 12px 24px rgba(0, 0, 0, .25); opacity: 0; }
        .toast.show { bottom: 20px; opacity: 1; transition: all .35s cubic-bezier(.2,.7,.2,1); }
        .add-to-cart-btn { background: var(--accent); color: white; border: none; padding: 8px 12px; border-radius: 8px; font-weight: 600; cursor: pointer; }
        .add-to-cart-btn:hover { background: var(--accent-2); }
        @media (max-width: 1024px) { .hero-grid { grid-template-columns: 1fr; } .grid { grid-template-columns: repeat(3, 1fr); } .footgrid { grid-template-columns: 1fr 1fr 1fr; } }
        @media (max-width: 720px) { .nav { min-height: 64px; } .headline { font-size: 32px; } .grid { grid-template-columns: repeat(2, 1fr); } .offers { grid-template-columns: 1fr; } .cta-banner { flex-direction: column; gap: 14px; align-items: flex-start; } .footgrid { grid-template-columns: 1fr 1fr; } }
        @media (max-width: 460px) { .grid { grid-template-columns: 1fr; } .chips { gap: 8px; } }
        
        /* The main content wrapper for non-home pages */
        .centered-content-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: calc(100vh - 72px - 142px); /* Adjust based on your header/footer heights */
            justify-content: center;
            gap: 20px;
        }

        .form-container, .login-modal-content, .checkout-summary, .recommendations, .records-table-container {
            background: var(--dark-card);
            color: #fff;
            padding: 32px 40px;
            border-radius: 14px;
            box-shadow: 0 6px 24px rgba(0,0,0,0.5);
            max-width: 800px;
            width: 90%;
            margin: auto;
            text-align: left;
            animation: fadeIn 0.5s ease-in-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .login-modal {
            display: none; position: fixed; z-index: 1000; left: 0; top: 0;
            width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.4);
            backdrop-filter: blur(5px);
        }
        .login-modal-content { margin: 15% auto; }
        .close-btn { color: #aaa; float: right; font-size: 28px; font-weight: bold; cursor: pointer; }
        .close-btn:hover, .close-btn:focus { color: #fff; text-decoration: none; }
        
        .form-container form, .login-modal-content form {
            display: grid;
            gap: 1.5rem;
            margin-top: 2rem;
        }

        .form-group {
            position: relative;
        }
        .form-group label {
            position: absolute;
            top: 50%;
            left: 1rem;
            transform: translateY(-50%);
            color: rgba(255, 255, 255, 0.7);
            pointer-events: none;
            transition: all 0.2s ease;
        }
        .form-group input, .form-group select {
            width: 100%;
            padding: 1rem;
            font-size: 1rem;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            color: #fff;
            transition: all 0.2s ease;
        }
        .form-group input:focus, .form-group input:not(:placeholder-shown), .form-group select:focus, .form-group select:not(:invalid) {
            outline: none;
            background: rgba(255, 255, 255, 0.2);
            box-shadow: 0 0 0 2px var(--accent);
        }
        .form-group input:focus + label, .form-group input:not(:placeholder-shown) + label,
        .form-group select:focus + label, .form-group select:not(:invalid) + label {
            top: 0;
            left: 0.5rem;
            font-size: 0.75rem;
            transform: translateY(-100%);
            color: var(--accent);
            padding: 0 0.5rem;
        }
        
        .form-container h2, .login-modal-content h2, .checkout-summary h2, .recommendations h3 {
            color: #ffcc29;
            text-align: center;
        }
        
        .checkout-summary, .recommendations, .records-table-container { margin-top: 20px; text-align: left; }
        .recommendations h3 { margin-bottom: 20px; }
        .rec-item { display: flex; align-items: center; gap: 15px; background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin-bottom: 10px; }
        .rec-item img { width: 80px; height: 80px; border-radius: 4px; object-fit: cover; }
        .rec-details { flex-grow: 1; }
        
        body.other-page {
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #fff;
            min-height: 100vh;
        }
        
        .records-table-container table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
            color: #fff;
        }
        .records-table-container th, .records-table-container td {
            padding: 12px 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        .records-table-container th {
            text-align: left;
            background: rgba(255, 255, 255, 0.1);
        }
        .records-table-container tr:nth-child(even) {
            background: rgba(255, 255, 255, 0.05);
        }
        .order-history-item {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body class="{{ body_class }}" style="background-image: url('{{ background_image }}');">
    <div class="toast" id="toast">Item added to cart!</div>
    <header class="header">
        <div class="container nav">
            <div class="brand">
                <div class="logo"></div> Swifty
            </div>
            <div class="nav-actions">
                <span class="pill">📍 <span id="city">Calcutta</span></span>
                <a href="/my_orders" id="myOrdersBtn" class="btn secondary" style="display:none;">My Orders</a>
                <a href="/view_cart" class="btn secondary">Cart <span id="cart-count">0</span></a>
                <button class="btn" id="loginBtn">Sign in</button>
            </div>
        </div>
    </header>
    <main class="container">
        <div class="centered-content-wrapper">
            {{ content }}
        </div>
    </main>
    <footer>
        <div class="footgrid">
            <div><div class="brand" style="margin-bottom:8px"><div class="logo"></div> Swifty</div>
                <div class="muted">Built as a learning project inspired by modern food delivery UIs.</div>
            </div>
            <div><b>Company</b><ul style="list-style:none;padding:0;margin:8px 0 0;display:grid;gap:10px">
                    <li><a href="#">About</a></li><li><a href="#">Careers</a></li><li><a href="#">Help & Support</a></li>
                </ul>
            </div>
            <div><b>Explore</b><ul style="list-style:none;padding:0;margin:8px 0 0;display:grid;gap:10px">
                    <li><a href="#">Restaurants near me</a></li><li><a href="#">Grocery stores</a></li><li><a href="#">Cuisines</a></li>
                </ul>
            </div>
            <div><b>Legal</b><ul style="list-style:none;padding:0;margin:8px 0 0;display:grid;gap:10px">
                    <li><a href="#">Terms</a></li><li><a href="#">Privacy</a></li><li><a href="#">Cookies</a></li>
                </ul>
            </div>
        </div>
    </footer>
    
    <div id="loginModal" class="login-modal">
      <div class="login-modal-content">
        <span class="close-btn">&times;</span>
        <h2>Sign In</h2>
        <form id="otpForm">
          <label for="email_otp">Email or Phone:</label>
          <input type="text" id="email_otp" name="email" required>
          <button type="submit">Send OTP</button>
        </form>
        <form id="verifyOtpForm" style="display:none;">
          <label for="otp">Enter OTP:</label>
          <input type="text" id="otp" name="otp" required>
          <button type="submit">Verify & Login</button>
        </form>
        <p id="loginMsg" style="color:red;"></p>
      </div>
    </div>
</body>
<script>
    const allFoodItems = """ + str(food_items_full) + """;
    
    // JS for cart, search, and login
    const grid = document.getElementById('grid');
    const toast = document.getElementById('toast');
    const searchInput = document.getElementById('search');
    const findBtn = document.getElementById('findBtn');
    const loginModal = document.getElementById('loginModal');
    const loginBtn = document.getElementById('loginBtn');
    const myOrdersBtn = document.getElementById('myOrdersBtn');
    const closeBtn = document.querySelector('.close-btn');
    const otpForm = document.getElementById('otpForm');
    const verifyOtpForm = document.getElementById('verifyOtpForm');
    const loginMsg = document.getElementById('loginMsg');
    const cartCount = document.getElementById('cart-count');

    function makeCard(r) {
        const el = document.createElement('article');
        el.className = 'card';
        el.innerHTML = `
            <div class="ratio"><img loading="lazy" src="${r.img}" alt="${r.name}"></div>
            <div class="content">
                <div class="title">${r.name}</div>
                <div class="muted">${r.tags}</div>
                <div class="meta">
                    <span class="badge rating">⭐ ${r.rating}</span>
                    <span class="badge">⏱️ ${r.time} mins</span>
                    <span class="badge">₹${r.price}</span>
                </div>
                <button class="add-to-cart-btn" data-food-id="${r.id}" data-food-name="${r.name}">Add to Cart</button>
            </div>`;
        const img = el.querySelector('img');
        img.addEventListener('load', () => { img.style.opacity = 1; el.querySelector('.ratio').style.animation = 'none'; });
        const addToCartButton = el.querySelector('.add-to-cart-btn');
        if (addToCartButton) {
            addToCartButton.addEventListener('click', addToCart);
        }
        return el;
    }
    
    function renderRestaurants(list) {
        if (!grid) return;
        grid.innerHTML = '';
        if (list.length > 0) {
            list.forEach(r => grid.appendChild(makeCard(r)));
        } else {
            grid.innerHTML = '<p style="color:red; text-align:center;">No restaurants found matching your search.</p>';
        }
    }
    document.addEventListener('DOMContentLoaded', () => {
        if(document.getElementById('grid')) {
             renderRestaurants(allFoodItems);
        }
    });

    function filter() {
        const q = searchInput.value.toLowerCase().trim();
        const filteredRestaurants = allFoodItems.filter(r => 
            r.name.toLowerCase().includes(q) || r.tags.toLowerCase().includes(q)
        );
        renderRestaurants(filteredRestaurants);
    }

    if (findBtn) {
        findBtn.addEventListener('click', filter);
    }
    if (searchInput) {
        searchInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') filter(); });
    }
    
    if(document.getElementById('offersBtn')) {
        document.getElementById('offersBtn').addEventListener('click', () => { document.getElementById('offers').scrollIntoView({ behavior: 'smooth' }); });
    }
    
    try {
        const tz = Intl.DateTimeFormat().resolvedOptions().timeZone || '';
        const city = tz.includes('/') ? tz.split('/').pop().replace('_', ' ') : 'your city';
        if(document.getElementById('city')) document.getElementById('city').textContent = city;
        if(document.getElementById('city2')) document.getElementById('city2').textContent = city;
    } catch (e) {
        if(document.getElementById('city')) document.getElementById('city').textContent = 'your city';
    }
    
    let toastTimer;
    function showToast(msg) {
        if (!toast) return;
        toast.textContent = msg;
        toast.classList.add('show');
        clearTimeout(toastTimer);
        toastTimer = setTimeout(() => toast.classList.remove('show'), 1800);
    }

    function updateCartCount() {
        if (!cartCount) return;
        fetch('/get_cart_count').then(r => r.json()).then(data => {
            cartCount.textContent = data.count;
        });
    }
    updateCartCount();

    function addToCart(e) {
        const foodId = e.target.dataset.foodId;
        fetch('/add_to_cart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 'food_id': foodId, 'quantity': 1 })
        }).then(response => response.json())
        .then(data => {
            showToast(data.message);
            updateCartCount();
        }).catch(() => {
            showToast("Failed to add to cart.");
        });
    }

    function checkLoginStatus() {
        fetch('/check_login_status')
        .then(response => response.json())
        .then(data => {
            if (data.logged_in) {
                loginBtn.style.display = 'none';
                myOrdersBtn.style.display = 'block';
            } else {
                loginBtn.style.display = 'block';
                myOrdersBtn.style.display = 'none';
            }
        });
    }
    checkLoginStatus();

    if(loginBtn) {
        loginBtn.onclick = function() { loginModal.style.display = "block"; }
    }
    if(closeBtn) {
        closeBtn.onclick = function() {
          loginModal.style.display = "none";
          loginMsg.textContent = "";
          otpForm.style.display = 'block';
          verifyOtpForm.style.display = 'none';
        }
    }
    window.onclick = function(event) {
      if (event.target == loginModal) {
        loginModal.style.display = "none";
        loginMsg.textContent = "";
        otpForm.style.display = 'block';
        verifyOtpForm.style.display = 'none';
      }
    }

    if(otpForm) {
        otpForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('email_otp').value;
            fetch('/send_otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 'email': email })
            }).then(response => response.json())
            .then(json => {
                if (json.success) {
                    loginMsg.style.color = 'green';
                    loginMsg.textContent = json.message;
                    otpForm.style.display = 'none';
                    verifyOtpForm.style.display = 'block';
                } else {
                    loginMsg.style.color = 'red';
                    loginMsg.textContent = json.message;
                }
            });
        });
    }

    if(verifyOtpForm) {
        verifyOtpForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('email_otp').value;
            const otp = document.getElementById('otp').value;
            fetch('/verify_otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 'email': email, 'otp': otp })
            }).then(response => response.json())
            .then(json => {
                if (json.success) {
                    loginMsg.style.color = 'green';
                    loginMsg.textContent = "Login successful!";
                    checkLoginStatus();
                    setTimeout(() => { loginModal.style.display = "none"; }, 1000);
                } else {
                    loginMsg.style.color = 'red';
                    loginMsg.textContent = json.message;
                }
            });
        });
    }
</script>
</html>
"""

# Homepage content HTML
home_content = """
<section class="hero">
    <div class="hero-grid">
        <div>
            <div class="chips">
                <li><a href="/add_customer">Add Customer</a></li>
                <li><a href="/add_food">Add Food</a></li>
                <li><a href="/view_records">View Records</a></li>
            </div>
            <div class="chips">
                <span class="chip">Fast delivery ⏱️ 30-40 mins</span>
                <span class="chip">No minimum order</span>
                <span class="chip">Live order tracking</span>
            </div>
            <h1 class="headline">Order food & groceries from the best near you.</h1>
            <p class="sub">Discover top restaurants, instant groceries, and late-night cravings — delivered with a dash of speed and a sprinkle of savings.</p>
            <div class="searchbar">
                <label class="input" aria-label="Search">
                    <span>🔎</span>
                    <input id="search" placeholder="Search for restaurant, item or more">
                </label>
                <button class="btn" id="findBtn">Find food</button>
            </div>
            <div class="scroller" aria-label="Popular categories">
                <article class="cat"><img src="https://images.unsplash.com/photo-1544025162-d76694265947?q=80&w=400&auto=format&fit=crop" alt="Biryani">
                    <div><b>Biryani</b><div class="muted">Smoky & flavorful</div></div>
                </article>
                <article class="cat"><img src="https://images.unsplash.com/photo-1550547660-d9450f859349?q=80&w=400&auto=format&fit=crop" alt="Pizza">
                    <div><b>Pizza</b><div class="muted">Cheesy goodness</div></div>
                </article>
                <article class="cat"><img src="https://images.unsplash.com/photo-1562967914-608f82629710?q=80&w=400&auto=format&fit=crop" alt="Burgers">
                    <div><b>Burgers</b><div class="muted">Grilled & juicy</div></div>
                </article>
                <article class="cat"><img src="https://images.unsplash.com/photo-1604908554028-0508d2b36446?q=80&w=400&auto=format&fit=crop" alt="Desserts">
                    <div><b>Desserts</b><div class="muted">Sweet treats</div></div>
                </article>
                <article class="cat"><img src="https://images.unsplash.com/photo-1551183053-bf91a1d81141?q=80&w=400&auto=format&fit=crop" alt="South Indian">
                    <div><b>South Indian</b><div class="muted">Crisp & comforting</div></div>
                </article>
            </div>
        </div>
        <div style="position:relative;min-height:420px">
            <img class="float" width="180" height="180" alt="Burger" src="https://images.unsplash.com/photo-1550547660-d9450f859349?q=80&w=360&auto=format&fit=crop">
            <img class="float" width="220" height="220" alt="Biryani" src="https://images.unsplash.com/photo-1544025162-d76694265947?q=80&w=440&auto=format&fit=crop">
            <img class="float" width="140" height="140" alt="Donut" src="https://images.unsplash.com/photo-1504674900247-0877df9cc836?q=80&w=280&auto=format&fit=crop">
        </div>
    </div>
</section>
<section class="offers section" id="offers">
    <div class="offer">🔥 50% OFF up to ₹120 on first 2 orders. Use code <u>NEW50</u></div>
    <div class="offer">💳 20% OFF with HDFC cards every Friday</div>
    <div class="offer">🛒 Instagroceries delivered in minutes — Try now</div>
</section>
<section class="section">
    <h2>Top picks in <span id="city2">Calcutta</span></h2>
    <p class="muted">Handpicked restaurants with great ratings and fast delivery.</p>
    <div class="grid" id="grid"></div>
</section>
<section class="cta-banner">
    <div>
        <b>Get it on the go.</b>
        <div class="muted">Track orders live, unlock deals, and reorder in seconds.</div>
    </div>
    <div class="store">
        <a href="#">📱 App Store</a>
        <a href="#">▶️ Play Store</a>
    </div>
</section>
<div class="chips">
    <li><a href="/add_employee">Add Employee</a></li>
</div>
"""

@app.route('/')
def home():
    return render_template_string(base_html.replace('{{ content }}', home_content).replace('{{ background_image }}', '').replace('{{ body_class }}', ''))

@app.route('/send_otp', methods=['POST'])
def send_otp():
    data = request.json
    email = data.get('email')
    if not email:
        return jsonify(success=False, message="Email/Phone is required.")
    otp = ''.join(random.choices(string.digits, k=6))
    otp_store[email] = {'otp': otp, 'timestamp': datetime.now()}
    return jsonify(success=True, message=f"OTP sent to {email}. (Demo OTP: {otp})")

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')
    if email not in otp_store or otp_store[email]['otp'] != otp:
        return jsonify(success=False, message="Invalid OTP. Please try again.")
    if datetime.now() - otp_store[email]['timestamp'] > timedelta(minutes=5):
        del otp_store[email]
        return jsonify(success=False, message="OTP has expired.")
    del otp_store[email]
    global logged_in_user
    logged_in_user = email
    return jsonify(success=True, message="Login successful.")

@app.route('/check_login_status')
def check_login_status():
    return jsonify(logged_in=logged_in_user is not None)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.json
    food_id = str(data.get('food_id'))
    quantity = int(data.get('quantity', 1))
    if food_id in cart:
        cart[food_id] += quantity
    else:
        cart[food_id] = quantity
    return jsonify(success=True, message="Item added to cart!")

@app.route('/get_cart_count', methods=['GET'])
def get_cart_count():
    count = sum(cart.values())
    return jsonify(count=count)

@app.route('/view_cart')
def view_cart():
    cart_items = []
    total_price = 0
    ordered_food_ids = list(cart.keys())
    
    for food_id, quantity in cart.items():
        item = next((f for f in food_items_full if str(f['id']) == food_id), None)
        if item:
            item_total = item['price'] * quantity
            total_price += item_total
            cart_items.append({
                'id': item['id'],
                'name': item['name'],
                'quantity': quantity,
                'price': item['price'],
                'total': item_total
            })
    
    ordered_tags = set()
    for item in cart_items:
        food_item = next(f for f in food_items_full if str(f['id']) == str(item['id']))
        tags = food_item['tags'].split(' • ')
        ordered_tags.update(tags)

    recommendations = [f for f in food_items_full if any(tag in f['tags'] for tag in ordered_tags) and str(f['id']) not in ordered_food_ids]
    recommendations.sort(key=lambda x: x['rating'], reverse=True)
    top_3_recs = recommendations[:3]
    
    recs_html = ""
    for rec in top_3_recs:
        recs_html += f"""
        <div class="rec-item">
            <img src="{rec['img']}" alt="{rec['name']}">
            <div class="rec-details">
                <strong>{rec['name']}</strong>
                <p style="margin:0; font-size:0.9em;">⭐ {rec['rating']} | ₹{rec['price']}</p>
                <p style="margin:0; font-size:0.8em; color:#ccc;">{rec['quality']}</p>
                <button class="add-to-cart-btn" data-food-id="{rec['id']}">Add to Cart</button>
            </div>
        </div>
        """

    cart_content = f"""
    <div class="checkout-summary">
        <h2>Your Cart</h2>
        <table style="width:100%; text-align:left;">
            <thead>
                <tr>
                    <th>Item</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
                {
                    ''.join(f"<tr><td>{item['name']}</td><td>{item['quantity']}</td><td>₹{item['price']}</td><td>₹{item['total']}</td></tr>" for item in cart_items)
                }
            </tbody>
        </table>
        <h3 style="text-align:right;">Total: ₹{total_price}</h3>
        <button onclick="window.location.href='/submit_order'" class="btn" style="width:100%; margin-top:20px;">Place Order</button>
        <a href="/">Continue Shopping</a>
    </div>
    <div class="recommendations">
        <h3>Our Top Recommendations for You</h3>
        <div>
            {recs_html if top_3_recs else '<p>No recommendations available right now.</p>'}
        </div>
    </div>
    """
    return render_template_string(base_html.replace('{{ content }}', cart_content).replace('{{ body_class }}', 'other-page').replace('{{ background_image }}', random.choice(background_images)))

@app.route('/submit_order')
def submit_order():
    if not cart:
        order_confirmation_content = f"""
        <div class="checkout-summary">
            <h2>Cart is Empty</h2>
            <p>Please add items to your cart before placing an order.</p>
            <a href="/">Go to Homepage</a>
        </div>
        """
    else:
        # Process the order and store it in order history
        global logged_in_user
        if logged_in_user not in order_history:
            order_history[logged_in_user] = []
        
        tracking_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        new_order = {
            'id': tracking_id,
            'items': list(cart.items()),
            'timestamp': datetime.now().isoformat(),
            'status_index': 0  # Initial status index
        }
        order_history[logged_in_user].append(new_order)

        # Clear the cart after order is "placed"
        cart.clear()

        order_confirmation_content = f"""
        <div class="checkout-summary">
            <h2>🎉 Order Placed Successfully!</h2>
            <p>Your order has been confirmed with Tracking ID: <strong>{tracking_id}</strong></p>
            <p>You can track your order status from the "My Orders" page.</p>
            <a href="/">Continue Shopping</a>
        </div>
        """
    return render_template_string(base_html.replace('{{ content }}', order_confirmation_content).replace('{{ body_class }}', 'other-page').replace('{{ background_image }}', random.choice(background_images)))

@app.route('/my_orders')
def my_orders():
    if not logged_in_user:
        my_orders_content = f"""
        <div class="checkout-summary">
            <h2>Access Denied</h2>
            <p>Please log in to view your orders.</p>
            <a href="/">Go to Homepage</a>
        </div>
        """
    else:
        my_orders_list = order_history.get(logged_in_user, [])

        orders_html = ""
        if not my_orders_list:
            orders_html = "<p style='text-align:center;'>You have no past orders.</p>"
        else:
            for order in my_orders_list:
                items_list = ""
                for food_id, qty in order['items']:
                    item = next(f for f in food_items_full if str(f['id']) == food_id)
                    items_list += f"<li>{item['name']} (x{qty})</li>"

                orders_html += f"""
                <div class="order-history-item">
                    <h4>Order ID: {order['id']}</h4>
                    <p><strong>Status:</strong> <span id="status-{order['id']}">{order_status_progression[order['status_index']]}</span></p>
                    <p><strong>Items:</strong></p>
                    <ul>{items_list}</ul>
                    <p><strong>Order Date:</strong> {order['timestamp'][:10]}</p>
                </div>
                """
        
        my_orders_content = f"""
        <div class="checkout-summary" style="max-width: 900px;">
            <h2>My Orders</h2>
            <div id="order-history-list">
                {orders_html}
            </div>
            <a href="/">Back to Home</a>
        </div>
        <script>
        const orderHistory = {jsonify(order_history).get_data(as_text=True)};
        const loggedInUser = '{logged_in_user}';
        const statusProgression = {jsonify(order_status_progression).get_data(as_text=True)};

        function updateOrderStatus() {{
            if (!loggedInUser || !orderHistory[loggedInUser]) return;

            orderHistory[loggedInUser].forEach(order => {{
                fetch('/get_order_status/' + order.id)
                .then(response => response.json())
                .then(data => {{
                    const statusSpan = document.getElementById('status-' + order.id);
                    if (statusSpan) {{
                        statusSpan.textContent = data.status;
                    }}
                }});
            }});
        }}

        setInterval(updateOrderStatus, 5000);
        </script>
        """
    return render_template_string(base_html.replace('{{ content }}', my_orders_content).replace('{{ body_class }}', 'other-page').replace('{{ background_image }}', random.choice(background_images)))

@app.route('/get_order_status/<tracking_id>')
def get_order_status(tracking_id):
    order = None
    for user_orders in order_history.values():
        order = next((o for o in user_orders if o['id'] == tracking_id), None)
        if order:
            break
    
    if not order:
        return jsonify(success=False, message="Order not found.")
    
    # Simulate status progression
    current_index = order['status_index']
    if current_index < len(order_status_progression) - 1:
        order['status_index'] = current_index + 1
    
    return jsonify(success=True, status=order_status_progression[order['status_index']])

@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    html = f"""
    <div class="form-container">
        <h2>Add Customer</h2>
        <form method="post" id="customerForm">
            <div class="form-group">
                <input name="c_id" type="number" id="c_id" placeholder=" " required>
                <label for="c_id">Customer ID</label>
            </div>
            <div class="form-group">
                <input name="name" id="name" placeholder=" " required>
                <label for="name">Name</label>
            </div>
            <div class="form-group">
                <input name="cphone" id="cphone" placeholder=" ">
                <label for="cphone">Phone</label>
            </div>
            <div class="form-group">
                <select name="payment" id="payment">
                    <option value="1">Credit Card</option>
                    <option value="2">Debit Card</option>
                </select>
                <label for="payment">Payment Method</label>
            </div>
            <div class="form-group">
                <input name="pstatus" id="pstatus" placeholder=" ">
                <label for="pstatus">Payment Status</label>
            </div>
            <div class="form-group">
                <input name="email" type="email" id="email" placeholder=" ">
                <label for="email">Email</label>
            </div>
            <div class="form-group">
                <input name="orderid" id="orderid" placeholder=" ">
                <label for="orderid">Order ID</label>
            </div>
            <div class="form-group">
                <input name="date" type="date" id="date">
                <label for="date">Date</label>
            </div>
            <button type="submit" class="btn secondary" style="width:100%">Submit</button>
        </form>
        <a href="/">Home</a>
        <p id="msg" style="text-align: center; margin-top: 1rem;"></p>
    </div>
    <script>
    const form = document.getElementById('customerForm');
    form.addEventListener('submit', function(e) {{
        e.preventDefault();
        const data = new URLSearchParams(new FormData(form));
        fetch('/add_customer', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest' }},
            body: data
        }}).then(response => response.json()).then(json => {{
            const msgElem = document.getElementById('msg');
            msgElem.style.color = json.success ? 'green' : 'red';
            msgElem.textContent = json.message;
            if(json.success) form.reset();
        }}).catch(() => {{
            const msgElem = document.getElementById('msg');
            msgElem.style.color = 'red';
            msgElem.textContent = 'Network error. Please try again.';
        }});
    }});
    </script>
    """
    if request.method == 'POST':
        try:
            mydb, mycursor = db_cursor()
            sqltxt = "INSERT INTO Customer (c_id, C_name, cphone, payment, pstatus, email, orderid, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            vals = (request.form['c_id'], request.form['name'], request.form['cphone'], request.form['payment'], request.form['pstatus'], request.form['email'], request.form['orderid'], request.form['date'])
            mycursor.execute(sqltxt, vals)
            mydb.commit()
            mycursor.close()
            mydb.close()
            return jsonify(success=True, message="Customer added successfully.")
        except Exception as e:
            return jsonify(success=False, message=f"Error: {e}")
    return render_template_string(base_html.replace('{{ content }}', html).replace('{{ body_class }}', 'other-page').replace('{{ background_image }}', random.choice(background_images)))

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    html = f"""
    <div class="form-container">
        <h2>Add Employee</h2>
        <form method="post" id="employeeForm">
            <div class="form-group">
                <input name="Emp_id" type="number" id="Emp_id" placeholder=" " required>
                <label for="Emp_id">Employee ID</label>
            </div>
            <div class="form-group">
                <input name="ename" id="ename" placeholder=" " required>
                <label for="ename">Name</label>
            </div>
            <div class="form-group">
                <input name="emp_g" id="emp_g" placeholder=" ">
                <label for="emp_g">Gender (M/F)</label>
            </div>
            <div class="form-group">
                <input name="eage" type="number" id="eage" placeholder=" ">
                <label for="eage">Age</label>
            </div>
            <div class="form-group">
                <input name="emp_phone" id="emp_phone" placeholder=" ">
                <label for="emp_phone">Phone</label>
            </div>
            <div class="form-group">
                <input name="pwd" type="password" id="pwd" placeholder=" ">
                <label for="pwd">Password</label>
            </div>
            <button type="submit" class="btn secondary" style="width:100%">Submit</button>
        </form>
        <a href="/">Home</a>
        <p id="msg" style="text-align: center; margin-top: 1rem;"></p>
    </div>
    <script>
    const form = document.getElementById('employeeForm');
    form.addEventListener('submit', function(e) {{
        e.preventDefault();
        const data = new URLSearchParams(new FormData(form));
        fetch('/add_employee', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest' }},
            body: data
        }}).then(response => response.json())
        .then(json => {{
            const msgElem = document.getElementById('msg');
            msgElem.style.color = json.success ? 'green' : 'red';
            msgElem.textContent = json.message;
            if(json.success) form.reset();
        }}).catch(() => {{
            const msgElem = document.getElementById('msg');
            msgElem.style.color = 'red';
            msgElem.textContent = 'Network error. Please try again.';
        }});
    }});
    </script>
    """
    if request.method == 'POST':
        try:
            mydb, mycursor = db_cursor()
            sqltxt = "INSERT INTO Employee (Emp_id, ename, emp_g, eage, emp_phone, pwd) VALUES (%s, %s, %s, %s, %s, %s)"
            vals = (request.form['Emp_id'], request.form['ename'], request.form['emp_g'], request.form['eage'], request.form['emp_phone'], request.form['pwd'])
            mycursor.execute(sqltxt, vals)
            mydb.commit()
            mycursor.close()
            mydb.close()
            return jsonify(success=True, message="Employee added successfully.")
        except Exception as e:
            return jsonify(success=False, message=f"Error: {e}")
    return render_template_string(base_html.replace('{{ content }}', html).replace('{{ body_class }}', 'other-page').replace('{{ background_image }}', random.choice(background_images)))

@app.route('/add_food', methods=['GET', 'POST'])
def add_food():
    html = f"""
    <div class="form-container">
        <h2>Add Food Item</h2>
        <form method="post" id="foodForm">
            <div class="form-group">
                <input name="Food_id" type="number" id="Food_id" placeholder=" " required>
                <label for="Food_id">Food ID</label>
            </div>
            <div class="form-group">
                <input name="Foodname" id="Foodname" placeholder=" " required>
                <label for="Foodname">Name</label>
            </div>
            <div class="form-group">
                <select name="Food_size" id="Food_size">
                    <option value="Small">Small</option>
                    <option value="Medium">Medium</option>
                    <option value="Large">Large</option>
                </select>
                <label for="Food_size">Size</label>
            </div>
            <div class="form-group">
                <input name="prize" type="number" step="0.01" id="prize" placeholder=" ">
                <label for="prize">Price</label>
            </div>
            <button type="submit" class="btn secondary" style="width:100%">Submit</button>
        </form>
        <a href="/">Home</a>
        <p id="msg" style="text-align: center; margin-top: 1rem;"></p>
    </div>
    <script>
    const form = document.getElementById('foodForm');
    form.addEventListener('submit', function(e) {{
        e.preventDefault();
        const data = new URLSearchParams(new FormData(form));
        fetch('/add_food', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest' }},
            body: data
        }}).then(response => response.json())
        .then(json => {{
            const msgElem = document.getElementById('msg');
            msgElem.style.color = json.success ? 'green' : 'red';
            msgElem.textContent = json.message;
            if(json.success) form.reset();
        }}).catch(() => {{
            const msgElem = document.getElementById('msg');
            msgElem.style.color = 'red';
            msgElem.textContent = 'Network error. Please try again.';
        }});
    }});
    </script>
    """
    if request.method == 'POST':
        try:
            mydb, mycursor = db_cursor()
            sqltxt = "INSERT INTO Food (Food_id, Foodname, Food_size, prize) VALUES (%s, %s, %s, %s)"
            vals = (request.form['Food_id'], request.form['Foodname'], request.form['Food_size'], request.form['prize'])
            mycursor.execute(sqltxt, vals)
            mydb.commit()
            mycursor.close()
            mydb.close()
            return jsonify(success=True, message="Food item added successfully.")
        except Exception as e:
            return jsonify(success=False, message=f"Error: {e}")
    return render_template_string(base_html.replace('{{ content }}', html).replace('{{ body_class }}', 'other-page').replace('{{ background_image }}', random.choice(background_images)))

@app.route('/place_order_form', methods=['GET', 'POST'])
def place_order_form():
    html = f"""
    <div class="form-container">
        <h2>Place Order</h2>
        <form method="post" id="orderForm">
            <div class="form-group">
                <input name="OrderF_id" type="number" id="OrderF_id" placeholder=" " required>
                <label for="OrderF_id">Order Food ID</label>
            </div>
            <div class="form-group">
                <input name="C_id" type="number" id="C_id" placeholder=" " required>
                <label for="C_id">Customer ID</label>
            </div>
            <div class="form-group">
                <input name="Emp_id" type="number" id="Emp_id" placeholder=" ">
                <label for="Emp_id">Employee ID</label>
            </div>
            <div class="form-group">
                <input name="Food_id" type="number" id="Food_id" placeholder=" " required>
                <label for="Food_id">Food ID</label>
            </div>
            <div class="form-group">
                <input name="Food_qty" type="number" id="Food_qty" placeholder=" ">
                <label for="Food_qty">Quantity</label>
            </div>
            <div class="form-group">
                <input name="Total_price" type="number" step="0.01" id="Total_price" placeholder=" ">
                <label for="Total_price">Total Price</label>
            </div>
            <button type="submit" class="btn secondary" style="width:100%">Submit</button>
        </form>
        <a href="/">Home</a>
        <p id="msg" style="text-align: center; margin-top: 1rem;"></p>
    </div>
    <script>
    const form = document.getElementById('orderForm');
    form.addEventListener('submit', function(e) {{
        e.preventDefault();
        const data = new URLSearchParams(new FormData(form));
        fetch('/place_order_form', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest' }},
            body: data
        }}).then(response => response.json())
        .then(json => {{
            const msgElem = document.getElementById('msg');
            msgElem.style.color = json.success ? 'green' : 'red';
            msgElem.textContent = json.message;
            if(json.success) form.reset();
        }}).catch(() => {{
            const msgElem = document.getElementById('msg');
            msgElem.style.color = 'red';
            msgElem.textContent = 'Network error. Please try again.';
        }});
    }});
    </script>
    """
    if request.method == 'POST':
        try:
            mydb, mycursor = db_cursor()
            sqltxt = "INSERT INTO OrderFood (OrderF_id, C_id, Emp_id, Food_id, Food_qty, Total_price) VALUES (%s, %s, %s, %s, %s, %s)"
            vals = (request.form['OrderF_id'], request.form['C_id'], request.form['Emp_id'], request.form['Food_id'], request.form['Food_qty'], request.form['Total_price'])
            mycursor.execute(sqltxt, vals)
            mydb.commit()
            mycursor.close()
            mydb.close()
            return jsonify(success=True, message="Order placed successfully.")
        except Exception as e:
            return jsonify(success=False, message=f"Error: {e}")
    return render_template_string(base_html.replace('{{ content }}', html).replace('{{ body_class }}', 'other-page').replace('{{ background_image }}', random.choice(background_images)))

@app.route('/view_records', methods=['GET', 'POST'])
def view_records():
    html = f"""
    <div class="form-container">
        <h2>View Records</h2>
        <form method="post" id="viewForm" style="display:flex; flex-wrap:wrap; gap: 1rem; justify-content:center;">
            <div class="form-group" style="flex-grow: 1;">
                <select name="view_choice" id="view_choice" required>
                    <option value="" disabled selected>Select an option</option>
                    <option value="employee_id">Employee by ID</option>
                    <option value="customer_name">Customer by Name</option>
                    <option value="all_foods">All Foods</option>
                    <option value="orders_by_food_id">Orders by Food ID</option>
                </select>
                <label for="view_choice">Choose Table</label>
            </div>
            <div class="form-group" style="flex-grow: 2;">
                <input name="search_value" id="search_value" placeholder=" ">
                <label for="search_value">Search Value</label>
            </div>
            <button type="submit" class="btn secondary">View Records</button>
        </form>
        <a href="/">Home</a>
    </div>
    <div id="results" class="records-table-container" style="display:none; text-align:center;"></div>
    <script>
    const form = document.getElementById('viewForm');
    const viewChoice = document.getElementById('view_choice');
    const searchValue = document.getElementById('search_value');
    const resultsDiv = document.getElementById('results');

    function toggleInput() {{
        if(viewChoice.value == 'all_foods' || viewChoice.value === ''){{
            searchValue.disabled = true;
            searchValue.value = '';
            searchValue.placeholder = '';
            searchValue.parentElement.style.opacity = '0.5';
        }} else {{
            searchValue.disabled = false;
            searchValue.placeholder = ' ';
            searchValue.parentElement.style.opacity = '1';
        }}
    }}
    viewChoice.addEventListener('change', toggleInput);
    toggleInput();

    form.addEventListener('submit', function(e){{
        e.preventDefault();
        resultsDiv.style.display = 'block';
        resultsDiv.innerHTML = "Loading...";
        const data = new URLSearchParams(new FormData(form));
        fetch('/view_records', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest' }},
            body: data
        }}).then(res => res.json())
        .then(json => {{
            if(json.success){{
                if(json.results.length === 0) {{
                    resultsDiv.innerHTML = "<p>No records found.</p>";
                    return;
                }}
                let table = '<table><thead><tr>';
                for(const col in json.results[0]){{ table += `<th>${{col}}</th>`; }}
                table += '</tr></thead><tbody>';
                for(const row of json.results){{
                    table += '<tr>';
                    for(const col in row){{ table += `<td>${{row[col]}}</td>`; }}
                    table += '</tr>';
                }}
                table += '</tbody></table>';
                resultsDiv.innerHTML = table;
            }} else {{
                resultsDiv.innerHTML = `<p style="color:red">{{json.message}}</p>`;
            }}
        }}).catch(() => resultsDiv.innerHTML = "<p style='color:red'>Network error occurred.</p>");
    }});
    </script>
    """
    if request.method == 'POST':
        try:
            mydb, mycursor = db_cursor()
            ch = request.form.get('view_choice')
            val = request.form.get('search_value')
            if ch == 'employee_id':
                sqltxt = "SELECT * FROM Employee WHERE Emp_id = %s"
                mycursor.execute(sqltxt, (val,))
            elif ch == 'customer_name':
                sqltxt = "SELECT * FROM Customer WHERE C_name = %s"
                mycursor.execute(sqltxt, (val,))
            elif ch == 'all_foods':
                sqltxt = "SELECT * FROM Food"
                mycursor.execute(sqltxt)
            elif ch == 'orders_by_food_id':
                sqltxt = "SELECT * FROM OrderFood WHERE Food_id = %s"
                mycursor.execute(sqltxt, (val,))
            else:
                return jsonify(success=False, message="Invalid choice")
            rows = mycursor.fetchall()
            columns = [i[0] for i in mycursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            mycursor.close()
            mydb.close()
            return jsonify(success=True, results=results)
        except Exception as e:
            return jsonify(success=False, message=f"Error: {e}")
    return render_template_string(base_html.replace('{{ content }}', html).replace('{{ body_class }}', 'other-page').replace('{{ background_image }}', random.choice(background_images)))


if __name__ == '__main__':
    app.run(debug=True)

