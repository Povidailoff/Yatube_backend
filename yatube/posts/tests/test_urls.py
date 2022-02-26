from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client

from .utils import PostsSetup

User = get_user_model()


class PostURLTests(PostsSetup):
    def setUp(self):
        # Авторизованный автор поста
        self.authorized_author = Client()
        self.authorized_author.force_login(self.user)

        # Авторизованный клиент не автор
        self.user = User.objects.create_user(username='TestUser2')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    templates = {
        '/': 'posts/index.html',
        '/group/test-slug/': 'posts/group_list.html',
        '/posts/1/': 'posts/post_detail.html',
        '/profile/TestUser/': 'posts/profile.html',
        '/create/': 'posts/create_post.html',
        '/posts/1/edit/': 'posts/create_post.html',
    }

    def test_templates_available(self):
        """Проверка доступности страниц"""

        for address in self.templates.keys():
            with self.subTest(address=address):
                response = self.authorized_author.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unassigned_pages(self):
        response = self.client.get('/404/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_used_right_templates(self):
        """Проверка шаблонов для авторизованных пользователей"""

        for address, template in self.templates.items():
            with self.subTest(address=address):
                response = self.authorized_author.get(address)
                self.assertTemplateUsed(response, template)

    def test_unathorized_redirect(self):
        """Проверка, что неавторизованных пользователей
           перенаправляет на страницу логина
        """
        authorized_templates = {
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }
        for address in authorized_templates.keys():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertRedirects(response, '/auth/login/?next=' + address)

    def test_only_author_can_edit(self):
        """Проверяем, что только автор поста может его редактировать.
           Другой пользователь перенаправляется на страницу записи
        """

        response = self.authorized_client.get('/posts/1/edit/')
        self.assertRedirects(response, '/posts/1/')
