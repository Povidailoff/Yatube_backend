from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse


User = get_user_model()


class UserViewTests(TestCase):
    def setUp(self):
        # Авторизованный клиент
        self.user = User.objects.create_user('TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    TEMPLATES = {
        'users/password_change_form.html':
        reverse('users:password_change'),

        'users/password_change_done.html':
        reverse('users:password_change_done'),

        'users/logged_out.html':
        reverse('users:logout'),

        'users/signup.html':
        reverse('users:signup'),

        'users/login.html':
        reverse('users:login'),

        'users/password_reset_form.html':
        reverse('users:password_reset'),

        'users/password_reset_done.html':
        reverse('users:password_reset_done'),

        'users/password_reset_confirm.html':
        reverse(
            'users:password_reset_confirm',
            kwargs={'uidb64': 'Mw', 'token': 'chto-ugodno'}
        ),

        'users/password_reset_complete.html':
        reverse('users:password_reset_complete'),

    }

    def test_users_page_accessible_by_name(self):
        """URL, генерируемый при помощи имени users:name, доступен."""

        for name in self.TEMPLATES.values():
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_users_page_uses_correct_template(self):
        """При запросе к users:name применяется шаблон users/name.html."""

        for template, name in self.TEMPLATES.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(name)
                self.assertTemplateUsed(response, template)
