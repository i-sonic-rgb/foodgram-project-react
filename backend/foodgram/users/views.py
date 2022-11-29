from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from rest_framework import (filters, permissions, status, viewsets)
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

from .permissions import IsSuperUserOrAdmin
from .serializers import (
    UserSerializer, NewUserCreateSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'id'
    search_fields = ('username',)
    pagination_class = LimitOffsetPagination
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserSerializer
        return NewUserCreateSerializer

    def get_user(self, user_id):
        return User.objects.filter(id=user_id)

    def get_queryset(self):
        if self.action == 'retrieve':
            return self.get_user(self.kwargs['id'])
        return User.objects.all()
    
    def get_permissions(self):
        if self.action == 'retrieve':
            self.permission_classes = (permissions.IsAuthenticated,)
        return super().get_permissions()

    @action(
        detail=False,
        methods=['PATCH', 'GET'],
        url_path='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        user = get_object_or_404(User, username=request.user.username)
        if request.method == 'GET':
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_200_OK
            )

        serializer = UserSerializer(
            instance=user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)
