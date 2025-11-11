from django.urls import include, path
from rest_framework.routers import DefaultRouter

# from .views import

router_v1 = DefaultRouter()

router_v1.register('reviews',)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/', include('djoser.urls.jwt')),

]
