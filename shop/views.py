import logging

from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import ReadOnlyOrAdmin

from .exceptions import ConflictError
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from .docs import (
    product_list,
    product_create,
    product_retrieve,
    product_update,
    product_delete,
)

logger = logging.getLogger(__name__)

def get_or_404(model, pk, label):
    try:
        return model.objects.get(pk=pk)
    except model.DoesNotExist:
        logger.warning("Не знайдено %s id=%s", model.__name__, pk)
        raise NotFound(f"{label} з id={pk} не знайдено.")

class CategoryListView(APIView):
    permission_classes = [ReadOnlyOrAdmin]

    def get(self, request):
        categories = Category.objects.order_by("id")
        return Response(CategorySerializer(categories, many=True).data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CategoryDetailView(APIView):
    permission_classes = [ReadOnlyOrAdmin]

    def get(self, request, pk):
        category = get_or_404(Category, pk, "Категорію")
        return Response(CategorySerializer(category).data)

    def put(self, request, pk):
        category = get_or_404(Category, pk, "Категорію")
        serializer = CategorySerializer(category, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        category = get_or_404(Category, pk, "Категорію")
        count = category.products.count()
        if count > 0:
            raise ConflictError(
                f"Неможливо видалити категорію «{category.name}», "
                f"оскільки в ній є прикраси: {count}. "
                f"Спочатку видаліть їх або перенесіть в іншу категорію."
            )
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductListView(APIView):
    permission_classes = [ReadOnlyOrAdmin]

    @product_list
    def get(self, request):
        logger.debug("Отримання списку прикрас")
        products = Product.objects.select_related("category").order_by("id")
        return Response(ProductSerializer(products, many=True).data)

    @product_create
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        logger.info("Створено прикрасу id=%s", product.pk)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductDetailView(APIView):
    permission_classes = [ReadOnlyOrAdmin]

    @product_retrieve
    def get(self, request, pk):
        logger.debug("Отримання прикраси id=%s", pk)
        product = get_or_404(Product, pk, "Прикрасу")
        return Response(ProductSerializer(product).data)

    @product_update
    def put(self, request, pk):
        product = get_or_404(Product, pk, "Прикрасу")
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info("Оновлено прикрасу id=%s", pk)
        return Response(serializer.data)

    @product_delete
    def delete(self, request, pk):
        product = get_or_404(Product, pk, "Прикрасу")
        product.delete()
        logger.info("Видалено прикрасу id=%s", pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductDetailView(APIView):
    permission_classes = [ReadOnlyOrAdmin]

    def get(self, request, pk):
        product = get_or_404(Product, pk, "Прикрасу")
        return Response(ProductSerializer(product).data)

    def put(self, request, pk):
        product = get_or_404(Product, pk, "Прикрасу")
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        product = get_or_404(Product, pk, "Прикрасу")
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)