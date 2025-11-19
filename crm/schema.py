import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from django.core.exceptions import ValidationError
from graphene_django.filter import DjangoFilterConnectionField
from crm.filters import CustomerFilter, ProductFilter, OrderFilter
from graphene import relay


from .models import Customer, Product, Order
from django.utils import timezone


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"
        interfaces = (relay.Node)


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"
        interfaces = (relay.Node)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"
        interfaces = (relay.Node)
class CreateCustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CreateCustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        # Validate unique email
        if Customer.objects.filter(email=input.email).exists():
            raise Exception("Email already exists.")

        # Basic phone validation
        if input.phone and not input.phone.replace("+", "").replace("-", "").isdigit():
            raise Exception("Invalid phone format.")

        customer = Customer(
            name=input.name,
            email=input.email,
            phone=input.phone
        )
        customer.save()

        return CreateCustomer(customer=customer, message="Customer created successfully")
class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CreateCustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, input):
        created = []
        errors = []

        for item in input:
            try:
                if Customer.objects.filter(email=item.email).exists():
                    errors.append(f"Email already exists: {item.email}")
                    continue

                customer = Customer(
                    name=item.name,
                    email=item.email,
                    phone=item.phone
                )
                customer.save()
                created.append(customer)

            except Exception as e:
                errors.append(str(e))

        return BulkCreateCustomers(customers=created, errors=errors)
class CreateProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(required=False)
class CreateProduct(graphene.Mutation):
    class Arguments:
        input = CreateProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        if input.price <= 0:
            raise Exception("Price must be positive")

        if input.stock is not None and input.stock < 0:
            raise Exception("Stock cannot be negative")

        product = Product(
            name=input.name,
            price=input.price,
            stock=input.stock or 0
        )
        product.save()

        return CreateProduct(product=product)
class CreateOrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime(required=False)
class CreateOrder(graphene.Mutation):
    class Arguments:
        input = CreateOrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID")

        if len(input.product_ids) == 0:
            raise Exception("At least one product must be selected")

        products = []
        total_amount = 0

        for pid in input.product_ids:
            try:
                product = Product.objects.get(id=pid)
                products.append(product)
                total_amount += float(product.price)
            except Product.DoesNotExist:
                raise Exception(f"Invalid product ID: {pid}")

        order = Order(
            customer=customer,
            total_amount=total_amount,
            order_date=input.order_date or timezone.now()
        )
        order.save()

        order.products.set(products)

        return CreateOrder(order=order)
class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(self, info):
        return Customer.objects.all()

    def resolve_products(self, info):
        return Product.objects.all()

    def resolve_orders(self, info):
        return Order.objects.all()
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
class Query(graphene.ObjectType):

    all_customers = DjangoFilterConnectionField(CustomerType, order_by=graphene.String())
    all_products = DjangoFilterConnectionField(ProductType, order_by=graphene.String())
    all_orders = DjangoFilterConnectionField(OrderType, order_by=graphene.String())

    def resolve_all_customers(self, info, order_by=None, **kwargs):
        qs = Customer.objects.all()
        if order_by:
            qs = qs.order_by(order_by)
        return qs

    def resolve_all_products(self, info, order_by=None, **kwargs):
        qs = Product.objects.all()
        if order_by:
            qs = qs.order_by(order_by)
        return qs

    def resolve_all_orders(self, info, order_by=None, **kwargs):
        qs = Order.objects.all()
        if order_by:
            qs = qs.order_by(order_by)
        return qs
