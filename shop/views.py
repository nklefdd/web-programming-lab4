from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from .exceptions import ConflictError
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


def get_or_404(model, pk, label):
    try:
        return model.objects.get(pk=pk)
    except model.DoesNotExist:
        raise NotFound(f"{label} з id={pk} не знайдено.")


class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.order_by("id")
        return Response(CategorySerializer(categories, many=True).data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CategoryDetailView(APIView):
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
    def get(self, request):
        products = Product.objects.select_related("category").order_by("id")
        return Response(ProductSerializer(products, many=True).data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductDetailView(APIView):
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
