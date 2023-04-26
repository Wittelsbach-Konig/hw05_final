from django.core.paginator import Paginator


def custom_paginator(request, post_list, DEFAULT_POSTS_NUMBER=10):
    """Функция, реализующая Пагинатор"""
    paginator = Paginator(post_list, DEFAULT_POSTS_NUMBER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
