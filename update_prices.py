#!/usr/bin/env python3
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Product

# Цены для товаров
prices = {
    # Печати
    'Печать организации': 1550,
    'Печать ИП': 1550,
    'Печать врача': 1200,
    'Печать по оттиску': 1800,
    'Факсимиле': 1000,
    
    # Штампы по размерам
    'Штамп 38x14 мм': 1000,
    'Штамп 47x18 мм': 1100,
    'Штамп 23x59 мм': 1300,
    'Штамп 50x30 мм': 1600,
    'Штамп 60x33 мм': 1600,
    'Штамп 60x40 мм': 1800,
    'Штамп 75x38 мм': 2100,
}

def update_prices():
    with app.app_context():
        for product_name, price in prices.items():
            product = Product.query.filter_by(name=product_name).first()
            if product:
                product.price = price
                print(f"Updated price for {product_name}: {price} руб.")
            else:
                print(f"Product not found: {product_name}")
        
        db.session.commit()
        print("All prices updated successfully!")

if __name__ == '__main__':
    update_prices()
