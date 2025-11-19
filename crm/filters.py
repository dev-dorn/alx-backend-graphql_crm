import django_filters
from .models import Customer, Product, Order

# -----------------------
# CUSTOMER FILTER
# -----------------------
class CustomerFilter(django_filters.FilterSet):
    name_icontains = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    email_icontains = django_filters.CharFilter(field_name="email", lookup_expr="icontains")
    created_at_gte = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")
    created_at_lte = django_filters.DateFilter(field_name="created_at", lookup_expr="lte")

    # Phone pattern filter
    phone_pattern = django_filters.CharFilter(method="filter_phone_pattern")

    def filter_phone_pattern(self, queryset, name, value):
        return queryset.filter(phone__startswith=value)

    class Meta:
        model = Customer
        fields = []


# -----------------------
# PRODUCT FILTER
# -----------------------
class ProductFilter(django_filters.FilterSet):
    name_icontains = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    price_gte = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_lte = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    stock_gte = django_filters.NumberFilter(field_name="stock", lookup_expr="gte")
    stock_lte = django_filters.NumberFilter(field_name="stock", lookup_expr="lte")

    class Meta:
        model = Product
        fields = []


# -----------------------
# ORDER FILTER
# -----------------------
class OrderFilter(django_filters.FilterSet):
    total_amount_gte = django_filters.NumberFilter(field_name="total_amount", lookup_expr="gte")
    total_amount_lte = django_filters.NumberFilter(field_name="total_amount", lookup_expr="lte")

    order_date_gte = django_filters.DateFilter(field_name="order_date", lookup_expr="gte")
    order_date_lte = django_filters.DateFilter(field_name="order_date", lookup_expr="lte")

    # Filter by customer name
    customer_name = django_filters.CharFilter(field_name="customer__name", lookup_expr="icontains")

    # Filter by product name
    product_name = django_filters.CharFilter(field_name="products__name", lookup_expr="icontains")

    # Filter orders containing a specific product ID
    product_id = django_filters.NumberFilter(field_name="products__id")

    class Meta:
        model = Order
        fields = []
