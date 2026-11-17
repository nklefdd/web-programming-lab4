from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from shop.views import ProductListView, ProductDetailView

product_urls = [
    path("api/products", ProductListView.as_view()),
    path("api/products/<int:pk>", ProductDetailView.as_view()),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/", include("shop.urls")),
    path(
        "api/schema",
        SpectacularAPIView.as_view(patterns=product_urls),
        name="schema",
    ),
    path("api/docs", SpectacularSwaggerView.as_view(url_name="schema")),
]