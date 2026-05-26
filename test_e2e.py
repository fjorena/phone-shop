import os, sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'electronic_shop.settings'
os.environ['PYTHONIOENCODING'] = 'utf-8'

import django
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from shop.models import Category, Product, Cart, CartItem, Review

User = get_user_model()
results = []

def check(label, cond, detail=''):
    results.append(('OK' if cond else 'FAIL', label, detail))

# 1. Home page
c = Client()
r = c.get('/')
cats = Category.objects.count()
check('1. Home page (3 kategori)',
      r.status_code == 200 and b'Phones' in r.content,
      f'HTTP {r.status_code} | {cats} kategori ne DB')

# 2. Faqja e kategorise
cat = Category.objects.filter(slug='phones').first()
r = c.get(f'/category/{cat.slug}/')
check('2. Faqja e kategorise (Phones)',
      r.status_code == 200,
      f'HTTP {r.status_code} | {cat.products.count()} produkte')

# 3. Detaji i produktit
prod = Product.objects.first()
r = c.get(f'/product/{prod.slug}/')
check('3. Detaji i produktit',
      r.status_code == 200,
      f'HTTP {r.status_code} | {prod.name}')

# 4. Search
r = c.get('/search/?q=phone')
check('4. Search kthon rezultate',
      r.status_code == 200 and b'Smartphone' in r.content,
      f'HTTP {r.status_code} | Smartphone in page: {b"Smartphone" in r.content}')

# 5. Anon ridrejtohet te login
r_cart = c.get('/cart/')
r_rev  = c.post(f'/product/{prod.id}/review/', {'rating': 5, 'comment': 'x'})
check('5. Anon -> redirect login',
      r_cart.status_code == 302 and r_rev.status_code == 302,
      f'Cart GET: {r_cart.status_code} | Review POST: {r_rev.status_code}')

# 6. Login dhe add to cart
User.objects.filter(username='e2euser').delete()
u = User.objects.create_user('e2euser', 'e@e.com', 'E2ePass123!')
grp, _ = Group.objects.get_or_create(name='Customers')
u.groups.add(grp)
Cart.objects.get_or_create(user=u)

c2 = Client()
c2.login(username='e2euser', password='E2ePass123!')
r = c2.post(f'/cart/add/{prod.id}/', follow=True)
cart = Cart.objects.get(user=u)
check('6. Add to cart (user i logged-in)',
      r.status_code == 200 and cart.total_items > 0,
      f'HTTP {r.status_code} | items={cart.total_items} | total={cart.total_price}')

# 7. Shto review
Review.objects.filter(user=u, product=prod).delete()
r = c2.post(f'/product/{prod.id}/review/',
            {'rating': '4', 'comment': 'Great product!'}, follow=True)
has_review = Review.objects.filter(user=u, product=prod).exists()
check('7. User logged-in mund te beje review',
      r.status_code == 200 and has_review,
      f'HTTP {r.status_code} | review saved: {has_review}')

# 8. Rating mesatar
prod.refresh_from_db()
check('8. Rating mesatar llogaritet',
      prod.total_reviews > 0 and prod.average_rating > 0,
      f'average_rating={prod.average_rating} | total_reviews={prod.total_reviews}')

# 9. Double review i bllokuar
c2.post(f'/product/{prod.id}/review/', {'rating': '5', 'comment': 'Again'}, follow=True)
count = Review.objects.filter(user=u, product=prod).count()
check('9. Double review i bllokuar',
      count == 1,
      f'Reviews per user = {count} (duhet te jete 1)')

# 10. Cart badge
cart.refresh_from_db()
check('10. Cart badge total_items i sakte',
      cart.total_items >= 1,
      f'total_items={cart.total_items} | total_price={cart.total_price}')

# 11. Admin panel
c3 = Client()
logged = c3.login(username='admin', password='admin123')
r_adm  = c3.get('/admin/')
check('11. Admin panel accessible',
      logged and r_adm.status_code == 200,
      f'login={logged} | HTTP {r_adm.status_code}')

# 12. About page ne Shqip
r = c.get('/about/')
check('12. About page (Shqip)',
      r.status_code == 200 and 'Rreth Nesh'.encode('utf-8') in r.content,
      f'HTTP {r.status_code} | "Rreth Nesh" ne faqe: {"Rreth Nesh".encode("utf-8") in r.content}')

# Rezultate
print()
for status, label, detail in results:
    mark = '[OK]  ' if status == 'OK' else '[FAIL]'
    print(f'  {mark}  {label}')
    print(f'           {detail}')
    print()

passed = sum(1 for s, _, _ in results if s == 'OK')
total  = len(results)
print(f'  ==============================')
print(f'  REZULTATI: {passed}/{total} teste kaluan')
if passed == total:
    print('  Gjithe testet kaluan!')
else:
    failed = [l for s, l, _ in results if s == 'FAIL']
    print(f'  Deshtuan: {", ".join(failed)}')
