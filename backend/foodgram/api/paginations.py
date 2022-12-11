from rest_framework import pagination


class RecipePagination(pagination.PageNumberPagination):
    '''Standart pagination. Used only for Recipe and Subscription viewsets.'''
    def get_page_size(self, request):
        if request.query_params.get('limit'):
            return request.query_params.get('limit')
        if request.query_params.get('is_in_shopping_cart'):
            return 100
        return 6
