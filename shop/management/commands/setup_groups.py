from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from shop.models import Category, Product, Review


class Command(BaseCommand):
    help = 'Creates Administrators and Customers permission groups'

    def handle(self, *args, **kwargs):
        shop_models = [Category, Product, Review]

        admin_group, created = Group.objects.get_or_create(name='Administrators')
        admin_perms = Permission.objects.filter(
            content_type__in=[ContentType.objects.get_for_model(m) for m in shop_models]
        )
        admin_group.permissions.set(admin_perms)
        self.stdout.write(self.style.SUCCESS(
            f'{"Created" if created else "Updated"} group "Administrators" '
            f'with {admin_perms.count()} permissions'
        ))

        customer_group, created = Group.objects.get_or_create(name='Customers')
        view_perms = Permission.objects.filter(
            content_type__in=[ContentType.objects.get_for_model(m) for m in shop_models],
            codename__startswith='view_'
        )
        customer_group.permissions.set(view_perms)
        self.stdout.write(self.style.SUCCESS(
            f'{"Created" if created else "Updated"} group "Customers" '
            f'with {view_perms.count()} permissions'
        ))
