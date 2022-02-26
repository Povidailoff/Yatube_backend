from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client


User = get_user_model()


class UsersURLTests(TestCase):
    def setUp(self):
        # Авторизованный клиент
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    FREE_TEMPLATES = {
        '/auth/logout/': 'users/logged_out.html',
        '/auth/signup/': 'users/signup.html',
        '/auth/login/': 'users/login.html',
        '/auth/password_reset/': 'users/password_reset_form.html',
        '/auth/password_reset/done/': 'users/password_reset_done.html',
        '/auth/reset/Mw/chto-ugodno/': 'users/password_reset_confirm.html',
        '/auth/reset/done': 'users/password_reset_complete.html',
    }

    AUTHORIZED_TEMPLATES = {
        '/auth/password_change/': 'users/password_change_form.html',
        '/auth/password_change/done/': 'users/password_change_done.html',
    }

    def test_templates_available(self):
        """Проверка доступности страниц"""

        ALL_TEMPLATES = {**self.AUTHORIZED_TEMPLATES, **self.FREE_TEMPLATES}
        for address in ALL_TEMPLATES.keys():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_templates_correct(self):
        """Проверяем, что вызываются правильные шаблоны"""

        ALL_TEMPLATES = {**self.AUTHORIZED_TEMPLATES, **self.FREE_TEMPLATES}
        for address, template in ALL_TEMPLATES.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_unathorized_redirect(self):
        """Проверяем, что анонимам предлагается войти"""

        for address in self.AUTHORIZED_TEMPLATES.keys():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertRedirects(response, '/auth/login/?next=' + address)
