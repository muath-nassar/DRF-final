from rest_framework.permissions import BasePermission
from rest_framework.request import HttpRequest

class IsManager(BasePermission):
    def has_permission(self, request: HttpRequest, view):
        if not request.user.is_anonymous:
            return request.user.groups.filter(name='Manager').exists()
        return False

class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_anonymous:
            return request.user.groups.filter(name='Delivery Crew').exists()
        return False

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        is_manager = request.user.groups.filter(name='Manager').exists()
        is_delivery_crew = request.user.groups.filter(name='Delivery Crew').exists()
        
        return not is_manager and not is_delivery_crew
    