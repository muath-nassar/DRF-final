from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsManager, IsCustomer
from .models import MenueItem, Cart, Order, OrderItem, Category
from .serializers import MenuItemSerializer, UserSerializer, CartSerializer, CartSerializerDTO, OrderSerializer, CategorySerializer
from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404
from decimal import Decimal
from datetime import datetime
# from django.http import HttpRequest
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


def is_manager(request):
    if request.user.groups.filter(name='Manager').exists():
        return True
    return False
        # return Response('Unauthorized access. Only Managers can access this endpoint', status=status.HTTP_403_FORBIDDEN)

class CategoryListCreate(ListCreateAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    def post(self, request, *args, **kwargs):
        if not is_manager(request):
            return Response({'error':'Unauthorized access. Only Managers can access this endpoint'},
                            status=status.HTTP_403_FORBIDDEN)
        return super().post(request, *args, **kwargs)

class CategorySingle(RetrieveUpdateDestroyAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        menu_items = MenueItem.objects.filter(category__id=pk)
        serialized_items = MenuItemSerializer(menu_items, many=True)
        return Response(serialized_items.data)

# @api_view(['GET'])
# def category_menu_items(request, pk):
#     if request.method == 'GET':
#         menu_items = MenueItem.objects.filter(category__id=pk)
#         serialized_items = MenuItemSerializer(menu_items, many=True)
#         return Response(serialized_items.data)
#     else:
#         return Response({'error': 'method not supported'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



class MenuItemsList(ListCreateAPIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    queryset = MenueItem.objects.all()
    serializer_class = MenuItemSerializer
    def post(self, request, *args, **kwargs):
        if not is_manager(request):
            return Response({'error':'Unauthorized access. Only Managers can access this endpoint'},
                            status=status.HTTP_403_FORBIDDEN)
        return super().post(request, *args, **kwargs)

class MenuItemSingle(RetrieveUpdateDestroyAPIView):
    queryset = MenueItem.objects.all()
    serializer_class = MenuItemSerializer

    def put(self, request, *args, **kwargs):
        if not is_manager(request):
            return Response('Unauthorized access. Only Managers can access this endpoint',
                            status=status.HTTP_403_FORBIDDEN)
        return super().put(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        if not is_manager(request):
            return Response('Unauthorized access. Only Managers can access this endpoint',
                            status=status.HTTP_403_FORBIDDEN)
        return super().patch(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        if not is_manager(request):
            return Response('Unauthorized access. Only Managers can access this endpoint',
                            status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

# Managers

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsManager])
def manager_list_add(request):
    if request.method == 'GET':
        managers = User.objects.filter(groups__name='Manager')
        data = []
        for manager in managers:
            data.append(UserSerializer(manager).data) 
        return Response(data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        user_to_add_pk = request.data.get('user_id')
        if user_to_add_pk:
            user = get_object_or_404(User, pk=user_to_add_pk)
            managers = Group.objects.get(name='Manager')
            managers.user_set.add(user)
            return Response(status=status.HTTP_201_CREATED)
        return Response('You should provide a valid user_id',status=status.HTTP_400_BAD_REQUEST)

    return Response(f'{request.method} is not allowed',status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsManager])
def manager_execlude(request, pk):
    user = get_object_or_404(User, pk=pk)
    managers = Group.objects.get(name='Manager')
    managers.user_set.remove(user)
    return Response(status=status.HTTP_200_OK)

# Delivery Crew

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsManager])
def delivery_crew_list_add(request):
    if request.method == 'GET':
        delivery_crew = User.objects.filter(groups__name='Delivery Crew')
        data = []
        for manager in delivery_crew:
            data.append(UserSerializer(manager).data) 
        return Response(data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        user_to_add_pk = request.data.get('user_id')
        if user_to_add_pk:
            user = get_object_or_404(User, pk=user_to_add_pk)
            delivery_crew = Group.objects.get(name='Delivery Crew')
            delivery_crew.user_set.add(user)
            return Response(status=status.HTTP_201_CREATED)
        return Response('You should provide a valid user_id',status=status.HTTP_400_BAD_REQUEST)

    return Response(f'{request.method} is not allowed',status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsManager])
def delivery_execlude(request, pk):
    user = get_object_or_404(User, pk=pk)
    delivery_crew = Group.objects.get(name='Delivery Crew')
    delivery_crew.user_set.remove(user)
    return Response(status=status.HTTP_200_OK)

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated, IsCustomer])
def cart_end_point(request):
    current_user = request.user
    if request.method == 'GET':
        carts = Cart.objects.filter(user=current_user)
        serialized_carts = CartSerializer(carts, many=True)
        print(serialized_carts)
        return Response(serialized_carts.data, status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        carts = Cart.objects.filter(user=current_user)
        carts.delete()
        return Response(status=status.HTTP_200_OK)
    elif request.method == 'POST':
        dto = CartSerializerDTO(data=request.data)
        dto.is_valid(raise_exception=True)
        quantity = Decimal(dto.data['quantity'])
        unit_price = Decimal(dto.data['unit_price'])
        price = quantity * unit_price
        appended = {'user': current_user.id, 'price': price}
        new_cart_data = dict(dto.data) | appended
        cart_serializer = CartSerializer(data=new_cart_data)
        cart_serializer.is_valid(raise_exception=True)
        cart_serializer.save()
        return Response(cart_serializer.data, status=status.HTTP_201_CREATED)
    
    # Orders

@permission_classes([IsCustomer])
@api_view(['POST', 'GET'])
def orders_endpoint(request):
    if request.method == 'POST':
        current_user = request.user
        cart_list = Cart.objects.filter(user=current_user)
        
        if cart_list.exists():
            serialized_carts = CartSerializer(cart_list, many=True)
            order_item_list = []
            total_price = 0
            new_order = Order(user=current_user, date=datetime.now().date())
            new_order.save()

            for cart_data in serialized_carts.data:
                cart = Cart.objects.get(id=cart_data['id'])
                order_item = OrderItem(
                    order=new_order,
                    menuitem=cart.menuitem,
                    quantity=cart.quantity,
                    unit_price=cart.unit_price,
                    price=cart.price
                )
                order_item.save()
                order_item_list.append(order_item)
                total_price += cart.price

            # Update the order with the total price
            new_order.total = total_price
            new_order.save()
            cart_list.delete()
            order_serializer = OrderSerializer(new_order)

            return Response(order_serializer.data, status=status.HTTP_200_OK)
        
        return Response({'error': 'No items in the cart'}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        current_user = request.user
        if is_manager(request):
            orders = Order.objects.all()
        else:
            orders = Order.objects.filter(user__id=current_user.id)
        serialized_orders = OrderSerializer(orders, many=True)
        return Response(serialized_orders.data, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def order_endpoint(request, order_id):
    current_user = request.user
    order =get_object_or_404(Order,pk=order_id)
    if request.method == 'GET':
        if order_id != current_user.id:
            return Response(
                {'error': f"This order (order_id={order_id}) doesn't belong to the user {current_user.username} id={current_user.id}."}, status=status.HTTP_401_UNAUTHORIZED)
        serialized_order = OrderSerializer(order)
        return Response(serialized_order.data, status=status.HTTP_200_OK)
    elif request.method in ['PATCH', 'PUT']:
        response = {}
        message = ''
        
        if 'delivery_crew' in request.data:
            is_current_user_deliver = request.user.groups.filter(name='Delivery Crew').exists()
            if is_current_user_deliver:
                return Response({'error': "user shouldn't be a deilivery crew"}, status=status.HTTP_401_UNAUTHORIZED)
            delivery_crew_id = request.data['delivery_crew']
            delivery_user = get_object_or_404(User, pk=delivery_crew_id)
            is_delivery_crew = delivery_user.groups.filter(name='Delivery Crew').exists()
            if not is_delivery_crew:
                return Response({'error': f"The user with user id {delivery_crew_id} is not a crew driver."},status=status.HTTP_400_BAD_REQUEST)
            delivery_user_serialized = UserSerializer(delivery_user)
            response['delivery crew'] = delivery_user_serialized.data
            message += 'delivery crew added. '
            order.delivery_crew = delivery_user
    
        if 'status' in request.data:
            order_status = request.data['status']
            if order_status not in ['0','1']:
                return Response({'error': 'status must be 0 or 1'}, status=status.HTTP_400_BAD_REQUEST)
            order.status = order_status
            message +=  f'new status = {order_status}.'

        order.save()
        serialized_order = OrderSerializer(order)
        return Response({'message': message,'order': serialized_order.data})
    if request.method == 'DELETE':
        if not is_manager(request):
            return Response({'error': 'You should be a manager to delete an order'}, status=status.HTTP_401_UNAUTHORIZED)
        order.delete()
        return Response({'message': 'Order deleted'})

        
        