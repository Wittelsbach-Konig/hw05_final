from http import HTTPStatus


def assert_func(self, client, templates_url_names):
    """Отдельная функция для тестирования с помощью subTest
    assertEqual и assertTemplateUsed"""
    for address, template in templates_url_names.items():
        with self.subTest(address=address):
            response = client.get(address)
            self.assertEqual(
                response.status_code,
                HTTPStatus.OK,
                f'Страница {template} недоступна!'
            )
            self.assertTemplateUsed(
                response,
                template,
                'Шаблон не совпадает с ссылкой!'
            )
