from rest_framework import mixins, viewsets


class ListRetrieveViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    '''Mixin class to get all or single instance of Model objects.'''
    pass


class ListViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    '''Mixin class to get all Model objects.'''
    pass
