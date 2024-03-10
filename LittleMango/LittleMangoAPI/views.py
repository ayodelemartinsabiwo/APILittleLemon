from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework import status, generics, permissions, viewsets
from .models import MenuItem, Category, Cart, Order
from django.db import IntegrityError
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import CategorySerializer, MenuItemsSerializer, CartSerializer, OrderSerializer, OrderItemSerializer, OrderItem
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, Group
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.pagination import PageNumberPagination
from rest_framework import permissions
from django.db import transaction
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
# Create your views here.

class IsManagerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Manager').exists()


class MenuItemsView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemsSerializer
    lookup_field = 'pk'
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsManagerPermission()]
        return [permissions.AllowAny()]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        #if status == status.HTTP_204_NO_CONTENT:
        #    return Response({'message': 'Menu item deleted successfuly!'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'message': 'Menu item deleted successfuly!'}, status=status.HTTP_200_OK)#Using HTTP 200 OK will make the delete msg showing both in the browser and insomnia.Rather using HTTP_204_NO_CONTENT, which will only show in the browser.

class MenuItemsListView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemsSerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]


    def get_permissions(self):
        if self.request.method in ['PUT', 'POST' 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsManagerPermission()]
        return [permissions.AllowAny()]


class CategoryView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    throttle_classes = [AnonRateThrottle, UserRateThrottle]




@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAdminUser])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def manager(request):
    if request.method == 'GET':
        manager_group = Group.objects.get(name='Manager')
        manager_users = manager_group.user_set.all()

        # Using a normal loop to build the list of usernames
        """
        manager_usernames = []
        for user in manager_users:
            manager_usernames.append(user.username)
        """
         # Assuming you want to return a list of usernames for managers. Using List comprehension
        manager_usernames = [user.username for user in manager_users]

        return Response({'managers': manager_usernames})
    username = request.data['username']
    if username:
        user = get_object_or_404(User, username=username)
        manager = Group.objects.get(name='Manager')
        if request.method == 'POST':
            manager.user_set.add(user)
        elif request.method == 'DELETE':
            manager.user_set.remove(user)
        return Response ({'message': 'Ok'})
    return Response({'message': 'error'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'DELETE'])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def manager_single(request, pk):
    try:
        manager_group = Group.objects.get(name='Manager')
        manager_user = manager_group.user_set.get(pk=pk)
    except Group.DoesNotExist:
        return Response({'error': 'Manager group not found'}, status=status.HTTP_404_NOT_FOUND)
    except manager_group.user_set.model.DoesNotExist:
        return Response({'error': 'Manager not found in the group'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response({'manager_username': manager_user.username}, status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        manager_user.delete()
        return Response({'message': 'Manager deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class DeliveryCrewView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        username = request.data.get('username')

        if not username:
            return Response({'error': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = get_user_model().objects.filter(username=username).first()

        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        delivery_crew_group = Group.objects.get(name='Delivery crew')
        delivery_crew_group.user_set.add(user)

        return Response({'message': 'User added to delivery crew group'}, status=status.HTTP_200_OK)


    def get(self, request, pk=None):
        if pk:
            # Check if the user with the given pk is a member of the delivery crew
            delivery_crew_group = Group.objects.get(name='Delivery crew')
            user = get_user_model().objects.filter(pk=pk, groups=delivery_crew_group).first()

            if not user:
                return Response({'message':'User not found in the delivery crew'}, status=status.HTTP_404_NOT_FOUND)

            return Response({'username': user.username}, status=status.HTTP_200_OK)
        else:
            # Perform logic for retrieving all users in the delivery crew group
            delivery_crew_group = Group.objects.get(name='Delivery crew')
            users = delivery_crew_group.user_set.all()
            user_data = [{'username': user.username} for user in users]
            return Response(user_data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        # Check if the user with the given pk is a member of the delivery crew
        delivery_crew_group = Group.objects.get(name='Delivery crew')
        user = get_user_model().objects.filter(pk=pk, groups=delivery_crew_group).first()

        if not user:
            return Response({'error': 'User not found in the delivery crew'}, status=status.HTTP_404_NOT_FOUND)

        # Remove the user from the delivery crew group
        delivery_crew_group.user_set.remove(user)

        return Response({'message': 'User removed from delivery crew group'}, status=status.HTTP_204_NO_CONTENT)

class CartView(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]


    def get(self, request):
        #username = request.GET.get('username')
        #is_user = request.user.user
        is_admin = request.user.is_staff

        if not is_admin:
            #user = get_object_or_404(User, username=username)
            cart_items = Cart.objects.filter(user=request.user)
        elif is_admin:
            cart_items = Cart.objects.all()
        else:
            return Response({'error':'user not found'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        user = request.user

        if user:
            cart_items = Cart.objects.filter(user=user)
            cart_items.delete()
            return Response({'message':'Cart items deleted Successfuly!'}, status=status.HTTP_200_OK)
        else:
            return Response({'error':'Cart Items not found!'}, status=status.HTTP_404_NOT_FOUND)



class OrderListView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    pagination_class = PageNumberPagination


    def get(self, request, *args, **kwargs):
        user = request.user
        admin = Group.objects.get(name='Manager')

        if admin in user.groups.all():
            # For managers, return all orders
            orders = Order.objects.all()
        elif user.groups.filter(name='Delivery Crew').exists():
            # For delivery crew, return orders assigned to them
            orders = Order.objects.filter(delivery_crew=user)
        else:
            # For customers, return their own orders
            orders = Order.objects.filter(user=user)

        #serializer = OrderSerializer(orders, many=True)
        #return Response(serializer.data, status=status.HTTP_200_OK)
        # Use pagination class to paginate the queryset

        page = self.paginate_queryset(orders)
        serializer = OrderSerializer(page, many=True)

        # Return paginated response
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        user = request.user
        carts = Cart.objects.filter(user=user)

        # Create order and order items
        order = Order.objects.create(user=user, date=timezone.now())

        # Assign the delivery crew to the order
        delivery_crew = request.user if request.user.groups.filter(name='Manager').exists() else None
        order.delivery_crew = delivery_crew
        order.save()



        for cart_item in carts:
            # Calculate price for each OrderItem
            order_item_price = cart_item.calculate_price()
            OrderItem.objects.create(
                order=order,
                menuitem=cart_item.menuitem,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                price=order_item_price # Set the price for the OrderItem
            )

        # Calculate total for the order
        order.calculate_total()

        # Delete items from the cart
        carts.delete()

        return Response({'message':'Order created successfully'}, status=status.HTTP_201_CREATED)

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def get(self, request, *args, **kwargs):
        order = self.get_object()

        # Check if the user is the customer, delivery crew, or manager
        user = request.user
        is_customer = user == order.user
        is_delivery_crew = user == order.delivery_crew
        is_manager = user.groups.filter(name='Manager').exists()

        if is_customer or is_delivery_crew or is_manager:
            order_items = order.order_items.all()
            serializer = OrderItemSerializer(order_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'You do not have permission to view this order'}, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        order = self.get_object()

        # Check if the user is a customer or manager
        user = request.user
        is_customer = user == order.user
        is_manager = user.groups.filter(name='Manager').exists()

        if is_customer or is_manager:
            # Allow the customer or manager to update the order
            serializer = OrderSerializer(order, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                # Check if a delivery crew is assigned and update status information
                if order.delivery_crew:
                    if order.status == 0:
                        message = 'Order is out for delivery'
                    elif order.status == 1:
                        message = 'Order has been delivered'
                    else:
                        message = 'Order updated successfully'
                else:
                    message = 'Order updated successfully'

                return Response({'message': message}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'You do not have permission to update this order'}, status=status.HTTP_403_FORBIDDEN)
