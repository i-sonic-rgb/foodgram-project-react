from rest_framework import pagination


class RecipePagination(pagination.PageNumberPagination):
    '''Standart pagination. Used only for Recipe and Subscription viewsets.'''
    page_size = 6
