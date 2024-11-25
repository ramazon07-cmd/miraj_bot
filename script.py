import os
import django
import requests

# Set up Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tbot.settings")  # Adjust to your project name
django.setup()

from all.models import ProductModel, CategoryModel  # Adjust the import based on your project structure

API_URL = "https://api.zon.uz/foodee/1000143276/categories-with-products"


def fetch_data():
    response = requests.get(API_URL)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()["data"]

def create_or_update_category(title):
    category = CategoryModel.objects.create()
    category.set_current_language('uz')
    category.title = title
    category.set_current_language('ru')
    category.title = title
    category.save()

    return category

def create_or_update_product(category, product_data):
    translations = product_data.get('nameText', {})
    image = product_data.get('images', [{}])[0].get('src', '')
    full_image_url = f"https://api.zon.uz{image}"
    price = product_data.get('sellingPrice', 0) / 100  

    try:
        product = ProductModel.objects.get(category=category, translations__title=translations.get('ru', ''))
        product.price = price
        product.description = product_data.get('description', '')
        product.image = full_image_url
        product.save()
    except ProductModel.DoesNotExist:
        product = ProductModel.objects.create(
            category=category,
            price=price,
            description=product_data.get('description', ''),
            image=full_image_url,
        )

    # Update translations
    product.set_current_language('uz')
    product.title = translations.get('uz', '')
    product.save()

    product.set_current_language('ru')
    product.title = translations.get('ru', '')
    product.save()

def import_products():
    data = fetch_data()
    for category_data in data:
        category_title = category_data["name"]
        print("category_title: ", category_title)
        category = create_or_update_category(category_title)
        for product_data in category_data.get("products", []):
            create_or_update_product(category, product_data)

if __name__ == "__main__":
    import_products()

