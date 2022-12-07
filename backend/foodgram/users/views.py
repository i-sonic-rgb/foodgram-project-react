from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import User
from .serializers import (NewUserCreateSerializer, UserResetPasswordSerializer,
                          UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'id'
    search_fields = ('username',)
    pagination_class = LimitOffsetPagination
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if (
            self.request.user.is_authenticated
            and self.action in ('list', 'retrieve')
        ):
            return UserSerializer
        return NewUserCreateSerializer

    def get_user(self, user_id):
        return User.objects.filter(id=user_id)

    @action(
        detail=False,
        methods=['GET'],
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
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserResetPasswordViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserResetPasswordSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if serializer.is_valid():
            current_password = serializer.data.get('current_password')
            if user.check_password(current_password):
                user.set_password(serializer.data.get('new_password'))
                user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'Current_password': ['Wrong password.']},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
