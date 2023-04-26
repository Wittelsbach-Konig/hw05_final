from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from core.assert_func.assert_func import assert_func


class StaticURLTests(TestCase):
    """Класс для тестирования статических ссылок"""

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        """Экземпляр клиента"""
        self.guest_client = Client()

    def test_pages(self):
        """Тестирование доступности страниц автора и технологий"""
        url_names = (
            '/about/author/',
            '/about/tech/',
        )
        for adress in url_names:
            with self.subTest():
                response = self.guest_client.get(adress)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    'Страницы автора и технологий не доступны',
                )

    def test_templates(self):
        """Тестирование шаблонов страниц"""
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(
                    response,
                    template,
                    ('Для страницы автора и технологий'
                     ' используются неверные шаблоны')
                )

    def test_namespaces(self):
        """Проверяем namespace в приложении about"""
        templates_url_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }
        assert_func(self,
                    self.guest_client,
                    templates_url_names)
