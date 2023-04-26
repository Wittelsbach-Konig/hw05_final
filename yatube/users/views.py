from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SingUp(CreateView):
    """View-класс регистрации

    Args:
        form_class : форма класса
        success_url : адрес для перенаправления
        template_name : имя шаблона html
    """

    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'
