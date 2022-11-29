from django.conf.urls import url
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet
from .views import SubscriptionViewSet

app_name = 'api'

v1_router = DefaultRouter()
v1_router.register('users', UserViewSet, basename='users')
v1_router.register(
    'users/subscriptions', SubscriptionViewSet, basename='subscriptions'
)


# auth_url = [
#     # path('signup/', SignupView.as_view(), name='signup'),
#     path('login', token, name='login')
# ]

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    # path('', include('djoser.urls')),
    path('', include(v1_router.urls)),
]
