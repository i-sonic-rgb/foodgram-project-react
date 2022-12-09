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
    '''CustomUser ViewSet Class. Separate serializers for creating new User.'''
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

    # Special action for ...api/users/me/ URL. Returns User object of
    # the authenticated User. On frontend data from this action put on
    # the website's header.
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
    '''Custom ViewSet for resetting password. Only POST available.'''
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserResetPasswordSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.is_valid(raise_exception=True)
        current_password = serializer.data.get('current_password')
        if user.check_password(current_password):
            user.set_password(serializer.validated_data.get('new_password'))
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'Current_password': ['Wrong password.']},
                        status=status.HTTP_400_BAD_REQUEST)
