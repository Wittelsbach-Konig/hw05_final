from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """View-класс об авторе
    Содержит описание автора проекта
    """

    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """View-класс про технологии
    Содержит описание использованных технологий в проекте
    """

    template_name = 'about/tech.html'
