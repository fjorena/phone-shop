from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render

from shop.models import Cart
from .forms import CustomUserCreationForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('shop:home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            customer_group, _ = Group.objects.get_or_create(name='Customers')
            user.groups.add(customer_group)

            Cart.objects.get_or_create(user=user)

            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Your account has been created.')
            return redirect('shop:home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')
