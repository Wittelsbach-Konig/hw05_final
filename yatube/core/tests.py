from http import HTTPStatus
from django.test import Client, TestCase


class CoreErrorTest(TestCase):
    """Тестирование шаблонов ошибки"""

    def setUp(self):
        """Создаём неавторизованный клиент"""
        self.guest_client = Client()

    def test_page_404(self):
        """Используется кастомный шаблон страницы для ошибки 404"""
        response = self.guest_client.get('/Alexandr_Beglov/')
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND,
            'Страница найдена. Танос сказал бы НЕВОЗМОЖНО.'
        )
        self.assertTemplateUsed(
            response,
            'core/404.html',
            'Шаблон 404 не найден'
        )
