from django.contrib import admin
from .models import Category, Product
from .models import NewsletterSubscriber, BlogPost, WishlistItem

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(NewsletterSubscriber)
admin.site.register(BlogPost)
admin.site.register(WishlistItem)