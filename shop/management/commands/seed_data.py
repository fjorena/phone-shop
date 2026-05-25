import shutil
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
from shop.models import Category, Product


STATIC_IMAGES = settings.BASE_DIR / 'static' / 'images'
MEDIA_PRODUCTS = settings.MEDIA_ROOT / 'products'
MEDIA_CATEGORIES = settings.MEDIA_ROOT / 'categories'


def copy_image(src_name, dest_dir):
    src = STATIC_IMAGES / src_name
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src_name
    if not dest.exists():
        shutil.copy2(src, dest)
    return dest_dir.name + '/' + src_name


CATEGORIES = [
    {
        'name': 'Phones',
        'description': 'Explore our latest smartphones with cutting-edge technology and premium features.',
        'image_file': 'cover_phone.jpg',
    },
    {
        'name': 'Laptops',
        'description': 'Explore our latest laptops with high performance and modern design.',
        'image_file': 'cover_laptop.jpg',
    },
    {
        'name': 'Accessories',
        'description': 'Discover useful accessories for your devices.',
        'image_file': 'cover_aksesor.jpg',
    },
]

PRODUCTS = [
    # --- Phones ---
    {
        'category': 'Phones',
        'name': 'Premium Smartphone X',
        'price': '1299.99',
        'description': 'Latest flagship with advanced features',
        'key_features': (
            '6.7" AMOLED display with 120Hz refresh rate\n'
            'Triple camera system (48MP, 12MP, 12MP)\n'
            '5G connectivity\n'
            'IP68 water resistance\n'
            'Fast charging - 65W\n'
            'Latest processor with 12GB RAM'
        ),
        'image_file': 'product_phone1.jpg',
        'stock': 15,
    },
    {
        'category': 'Phones',
        'name': 'Smart Phone Pro',
        'price': '999.99',
        'description': 'Professional-grade smartphone for power users',
        'key_features': (
            '6.5" OLED display\n'
            'Dual camera 50MP+12MP\n'
            '5G\n'
            '8GB RAM\n'
            '128GB storage\n'
            'Wireless charging'
        ),
        'image_file': 'product_phone2.jpg',
        'stock': 20,
    },
    {
        'category': 'Phones',
        'name': 'Compact Mobile Z',
        'price': '699.99',
        'description': 'Compact yet powerful smartphone for everyday use',
        'key_features': (
            '6.1" display\n'
            '48MP camera\n'
            '5G\n'
            '6GB RAM\n'
            '128GB storage\n'
            'All-day battery'
        ),
        'image_file': 'product_phone3.jpg',
        'stock': 25,
    },
    # --- Laptops ---
    {
        'category': 'Laptops',
        'name': 'UltraBook Pro 14',
        'price': '1199.99',
        'description': 'Thin and powerful ultrabook for work and travel',
        'key_features': (
            '14" IPS display with 300 nits brightness\n'
            'Intel Core i7 processor\n'
            '16GB RAM and 512GB SSD\n'
            'Thunderbolt 4 connectivity\n'
            'Up to 12 hours battery life'
        ),
        'image_file': 'product_laptop1.webp',
        'stock': 10,
    },
    {
        'category': 'Laptops',
        'name': 'Gaming Notebook V',
        'price': '1599.99',
        'description': 'High-end gaming performance with vibrant display',
        'key_features': (
            '15.6" Full HD 144Hz\n'
            'RTX 4060 GPU\n'
            'Intel i7 12th gen\n'
            '16GB DDR5\n'
            '1TB NVMe SSD\n'
            'RGB backlit keyboard'
        ),
        'image_file': 'product_laptop2.webp',
        'stock': 8,
    },
    {
        'category': 'Laptops',
        'name': 'Business Mate 15',
        'price': '899.99',
        'description': 'Reliable business laptop with long battery life',
        'key_features': (
            '15.6" FHD display\n'
            'Intel i5\n'
            '8GB RAM\n'
            '256GB SSD\n'
            'Fingerprint reader\n'
            '10+ hours battery'
        ),
        'image_file': 'product_laptop3.webp',
        'stock': 12,
    },
    # --- Accessories ---
    {
        'category': 'Accessories',
        'name': 'Wireless Charging Pad',
        'price': '39.99',
        'description': 'Fast charging pad for phones and earbuds',
        'key_features': (
            'Qi wireless charging standard\n'
            'Fast charging up to 15W\n'
            'Compact and portable design\n'
            'LED charging indicator'
        ),
        'image_file': 'product_aksesor1.jpg',
        'stock': 50,
    },
    {
        'category': 'Accessories',
        'name': 'Noise-Canceling Headset',
        'price': '149.99',
        'description': 'Comfortable headset for calls and entertainment',
        'key_features': (
            'Active noise cancellation\n'
            '30-hour battery\n'
            'Bluetooth 5.3\n'
            'Premium audio drivers\n'
            'Foldable design'
        ),
        'image_file': 'product_aksesor2.jpg',
        'stock': 30,
    },
    {
        'category': 'Accessories',
        'name': 'Portable Power Bank',
        'price': '49.99',
        'description': 'Compact power bank for charging on the go',
        'key_features': (
            '20000mAh capacity\n'
            'Dual USB output\n'
            'Fast charge 18W\n'
            'Lightweight design\n'
            'LED status indicator'
        ),
        'image_file': 'product_aksesor3.jpg',
        'stock': 40,
    },
]


class Command(BaseCommand):
    help = 'Seeds the database with categories and products'

    def handle(self, *args, **kwargs):
        # Categories
        category_objects = {}
        for data in CATEGORIES:
            image_path = copy_image(data['image_file'], MEDIA_CATEGORIES)
            cat, created = Category.objects.get_or_create(
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'image': image_path,
                },
            )
            category_objects[cat.name] = cat
            label = 'Created' if created else 'Already exists'
            self.stdout.write(f'  [{label}] Category: {cat.name}')

        # Products
        for data in PRODUCTS:
            cat = category_objects[data['category']]
            image_path = copy_image(data['image_file'], MEDIA_PRODUCTS)
            product, created = Product.objects.get_or_create(
                name=data['name'],
                defaults={
                    'category': cat,
                    'price': data['price'],
                    'description': data['description'],
                    'key_features': data['key_features'],
                    'image': image_path,
                    'stock': data['stock'],
                },
            )
            label = 'Created' if created else 'Already exists'
            self.stdout.write(f'  [{label}] Product: {product.name} (${product.price})')

        self.stdout.write(self.style.SUCCESS('\nSeed data created successfully!'))
