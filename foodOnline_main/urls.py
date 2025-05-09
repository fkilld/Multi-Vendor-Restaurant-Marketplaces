# Import Django's admin module to access admin site functionality
from django.contrib import admin
# Import path for defining URL patterns and include for including other URL patterns
from django.urls import path, include
# Import views from the current directory (main project views)
from . import views
# Import settings module to access project configuration
from django.conf import settings
# Import static helper function to serve media files during development
from django.conf.urls.static import static
# Import marketplace views with an alias for direct reference
from marketplace import views as MarketplaceViews


urlpatterns = [
    # URL pattern for Django admin interface
    path('admin/', admin.site.urls),
    # Root URL pattern that maps to the home page view
    path('', views.home, name='home'),
    # Include all URL patterns from the accounts app at the root level
    path('', include('accounts.urls')),

    # Include all marketplace app URL patterns under the 'marketplace/' prefix
    path('marketplace/', include('marketplace.urls')),

    # CART - URL pattern for the shopping cart functionality
    path('cart/', MarketplaceViews.cart, name='cart'),
    # SEARCH - URL pattern for the search functionality
    path('search/', MarketplaceViews.search, name='search'),

    # CHECKOUT - URL pattern for the checkout process
    path('checkout/', MarketplaceViews.checkout, name='checkout'),

    # ORDERS - Include all orders app URL patterns under the 'orders/' prefix
    path('orders/', include('orders.urls')),

    # Add URL patterns to serve media files during development
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
