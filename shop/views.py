from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Q, Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, TemplateView

from .forms import ReviewForm
from .models import Cart, CartItem, Category, Product, Review


class HomeView(TemplateView):
    template_name = 'shop/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all()[:3]
        ctx['featured_products'] = (
            Product.objects
            .select_related('category')
            .order_by('-created_at')[:6]
        )
        return ctx


class AboutView(TemplateView):
    template_name = 'shop/about.html'


class CategoryView(DetailView):
    model = Category
    template_name = 'shop/category.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['products'] = (
            self.object.products
            .select_related('category')
            .order_by('-created_at')
        )
        return ctx


class ProductDetailView(DetailView):
    model = Product
    template_name = 'shop/product_detail.html'
    context_object_name = 'product'
    queryset = Product.objects.select_related('category').prefetch_related(
        Prefetch('reviews', queryset=Review.objects.select_related('user'))
    )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['reviews'] = self.object.reviews.all()
        ctx['review_form'] = ReviewForm()
        ctx['user_has_reviewed'] = (
            self.request.user.is_authenticated
            and self.object.reviews.filter(user=self.request.user).exists()
        )
        return ctx


class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'shop/cart.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        ctx['cart'] = cart
        ctx['items'] = cart.items.select_related('product__category').all()
        return ctx


class SearchView(TemplateView):
    template_name = 'shop/search_results.html'
    RESULTS_PER_PAGE = 9

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        ctx['query'] = query

        if query:
            qs = (
                Product.objects
                .select_related('category')
                .filter(Q(name__icontains=query) | Q(description__icontains=query))
                .order_by('name')
            )
        else:
            qs = Product.objects.none()

        paginator = Paginator(qs, self.RESULTS_PER_PAGE)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        ctx['page_obj']   = page_obj
        ctx['results']    = page_obj
        ctx['paginator']  = paginator
        ctx['total_count'] = paginator.count
        return ctx


@login_required
def add_to_cart(request, product_id):
    if request.method != 'POST':
        return redirect('shop:home')

    product = get_object_or_404(Product, id=product_id)

    if product.stock < 1:
        messages.error(request, f'"{product.name}" is out of stock.')
        return redirect('shop:product_detail', slug=product.slug)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        if item.quantity >= product.stock:
            messages.warning(
                request,
                f'Cannot add more — only {product.stock} units of "{product.name}" in stock.'
            )
        else:
            item.quantity += 1
            item.save()
            messages.success(request, f'"{product.name}" quantity updated to {item.quantity}.')
    else:
        messages.success(request, f'"{product.name}" added to cart!')

    return redirect('shop:cart')


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    name = item.product.name
    item.delete()
    messages.success(request, f'"{name}" removed from cart.')
    return redirect('shop:cart')


@login_required
def add_review(request, product_id):
    if request.method != 'POST':
        return redirect('shop:home')

    product = get_object_or_404(Product, id=product_id)

    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        try:
            review.save()
            messages.success(request, 'Your review has been submitted. Thank you!')
        except IntegrityError:
            messages.warning(request, 'You have already reviewed this product.')
    else:
        messages.error(request, 'Please select a rating and write a comment.')

    return redirect('shop:product_detail', slug=product.slug)
