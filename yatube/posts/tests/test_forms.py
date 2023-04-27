import shutil
import tempfile

from http import HTTPStatus
from urllib.parse import urljoin

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    """Класс для тестирования Forms приложения Post"""

    SMALL_GIF = (
        b'\x47\x49\x46\x38\x39\x61\x02\x00'
        b'\x01\x00\x80\x00\x00\x00\x00\x00'
        b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
        b'\x00\x00\x00\x2C\x00\x00\x00\x00'
        b'\x02\x00\x01\x00\x00\x02\x02\x0C'
        b'\x0A\x00\x3B'
    )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        """Создаем объект класса Group"""
        cls.group = Group.objects.create(
            title=('Заголовок для тестовой группы'),
            slug='test_slug',
            description='Тестовое описание'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        """Удаляем файлы из media после тестирования"""
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Создаём авторизованный клиент"""
        self.user = User.objects.create_user(username='Alex_Beglov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()

    def test_create_post_with_group(self):
        """
        Проверяем что будет создана запись в базе данных
        при отправки формы создания поста с группой
        """
        form_data = {
            'text': 'Данные из формы',
            'group': PostCreateFormTests.group.id
        }
        filter_params = {
            **form_data,
            'author': self.user.id,
        }
        count_posts = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={
                    'username': self.user.get_username(),
                }
            )
        )
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertTrue(
            Post.objects.filter(**filter_params).exists()
        )

    def test_create_post_without_group(self):
        """
        Проверяем что будет создана запись в базе данных
        при отправки формы создания поста без группы
        """
        form_data = {
            'text': 'Данные из формы',
        }
        filter_params = {
            **form_data,
            'group': None,
            'author': self.user.id,
        }
        count_posts = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={
                    'username': self.user.get_username(),
                }
            )
        )
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertTrue(
            Post.objects.filter(**filter_params).exists()
        )

    def test_create_post_with_image(self):
        """
        Проверяем что будет создана запись в базе данных
        при отправки формы создания поста с картинкой
        """
        small_gif = self.SMALL_GIF
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Пост с картинкой',
            'image': uploaded
        }
        filter_params = {
            'text': 'Пост с картинкой',
            'author': self.user.id,
            'group': None,
            'image': f'posts/{form_data["image"].name}'
        }
        count_posts = Post.objects.count()
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={
                    'username': self.user.get_username(),
                }
            )
        )
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertTrue(
            Post.objects.filter(**filter_params).exists()
        )

    def test_create_post_guest(self):
        """
        Проверяем что при POST запросе не будет
        создаваться новый пост для неавторизованного пользователя
        """
        count_posts = Post.objects.count()
        form_data = {
            'text': 'Данные из формы',
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            urljoin(
                reverse('users:login'),
                '?next=/create/'
            )
        )
        self.assertEqual(Post.objects.count(), count_posts)

    def test_edit_post_authorized(self):
        """
        Проверяем что со страницы редактирования поста
        происходят изменения в базе данных
        """
        small_gif = self.SMALL_GIF
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        post = Post.objects.create(
            author=self.user,
            text='Тестовая запись для тестового поста.',
            group=PostCreateFormTests.group
        )
        form_data = {
            'text': 'Измененный текст',
            'group': PostCreateFormTests.group.id,
            'image': uploaded
        }
        response_edit = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': post.id}
            ),
            data=form_data,
            follow=True,
        )
        post_edited = Post.objects.get(id=PostCreateFormTests.group.id)
        assert_dict = {
            response_edit.status_code: HTTPStatus.OK,
            post_edited.text: form_data['text'],
            post_edited.group: form_data['group'],
            post_edited.pub_date: post.pub_date,
            post_edited.author: post.author,
            post_edited.image: f'posts/{form_data["image"].name}'
        }
        for value, expected in assert_dict.items():
            with self.subTest(value=value):
                self.assertEqual(
                    value,
                    expected,
                    f'{value} не соответствует {expected}'
                )

    def test_edit_post_guest(self):
        """
        При POST запросе неавторизованного
        пользователя пост не будет отредактирован
        """
        small_gif = self.SMALL_GIF
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        post = Post.objects.create(
            author=User.objects.create_user(username='test_name',
                                            email='test@yandex.ru',
                                            password='test_pass',),
            text='Тестовая запись для тестового поста.',
            group=PostCreateFormTests.group,
            image=uploaded
        )
        form_data = {
            'text': 'Измененный текст',
            'group': PostCreateFormTests.group.id,
        }
        redirect_guest = {
            'viewname': 'users:login',
        }
        redirect_login = f'?next=/posts/{post.id}/edit/'
        response = self.guest_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': post.id}
            ),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            urljoin(
                reverse(**redirect_guest),
                redirect_login
            )
        )
        post_edited = Post.objects.get(id=PostCreateFormTests.group.id)
        assert_dict = {
            post_edited.text: post.text,
            post_edited.group: post.group,
            post_edited.pub_date: post.pub_date,
            post_edited.author: post.author,
            post_edited.image: post.image
        }
        for value, expected in assert_dict.items():
            with self.subTest(value=value):
                self.assertEqual(
                    value,
                    expected,
                    f'{value} не соответствует {expected}'
                )

    def test_edit_post_authorized(self):
        """При POST запросе не автора пост не будет отредактирован"""
        small_gif = self.SMALL_GIF
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        post = Post.objects.create(
            author=User.objects.create_user(username='test_name',
                                            email='test@yandex.ru',
                                            password='test_pass',),
            text='Тестовая запись для тестового поста.',
            group=PostCreateFormTests.group,
            image=uploaded
        )
        form_data = {
            'text': 'Измененный текст',
            'group': PostCreateFormTests.group.id
        }
        redirect_post = {
            'viewname': 'posts:post_detail',
            'kwargs': {
                'post_id': post.pk
            }
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': post.id}
            ),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(**redirect_post)
        )
        post_edited = Post.objects.get(id=PostCreateFormTests.group.id)
        assert_dict = {
            post_edited.text: post.text,
            post_edited.group: post.group,
            post_edited.pub_date: post.pub_date,
            post_edited.author: post.author,
            post_edited.image: post.image
        }
        for value, expected in assert_dict.items():
            with self.subTest(value=value):
                self.assertEqual(
                    value,
                    expected,
                    f'{value} не соответствует {expected}'
                )

    def test_add_comment_guest(self):
        """
        Не авторизованный пользователь не может оставлять комментарии
        """
        comments = Comment.objects.count()
        post = Post.objects.create(
            author=User.objects.create_user(username='test_name',
                                            email='test@yandex.ru',
                                            password='test_pass',),
            text='Тестовая запись для тестового поста.',
            group=PostCreateFormTests.group,
        )
        form_data = {
            'text': 'Измененный текст',
        }
        redirect_guest = {
            'viewname': 'users:login',
        }
        redirect_login = f'?next=/posts/{post.id}/comment/'
        response = self.guest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': post.id}
            ),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            urljoin(
                reverse(**redirect_guest),
                redirect_login
            )
        )
        self.assertEqual(Comment.objects.count(), comments)
        self.assertFalse(
            Comment.objects.filter(text=form_data["text"]).exists()
        )

    def test_add_comment_authorized(self):
        """
        Авторизованный пользователь может оставлять комментарии
        """
        comments = Comment.objects.count()
        post = Post.objects.create(
            author=User.objects.create_user(username='test_name',
                                            email='test@yandex.ru',
                                            password='test_pass',),
            text='Тестовая запись для тестового поста.',
            group=PostCreateFormTests.group,
        )
        redirect_post = {
            'viewname': 'posts:post_detail',
            'kwargs': {
                'post_id': post.pk
            }
        }
        form_data = {
            'text': 'Измененный текст',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': post.id}
            ),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse(**redirect_post)
        )
        self.assertEqual(Comment.objects.count(), comments + 1)
        self.assertTrue(
            Comment.objects.filter(text=form_data["text"]).exists()
        )
