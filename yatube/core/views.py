from django.shortcuts import render


def page_not_found(request, exception):
    """Если запрашиваемая страница не найдена"""
    return render(
        request,
        'core/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    """Ошибка сервера"""
    return render(request, 'core/500.html', status=500)


def csrf_failure(request, reason=''):
    """ошибка проверки CSRF, запрос отклонён"""
    return render(request, 'core/403csrf.html')
