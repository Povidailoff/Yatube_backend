from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class PostFormTests(TestCase):
    def test_creating_user(self):
        """Проверяем, что создается новый пользователь"""

        users_count = User.objects.count()
        form_data = {
            'first_name': 'Shrek',
            'last_name': 'Islove',
            'username': 'Shreck',
            'email': 'Shrek@is.love',
            'password1': '123456Q2',
            'password2': '123456Q2',
        }
        response = self.client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        # Проверяем редирект
        self.assertRedirects(response, reverse('posts:index'))
        # Проверяем, что пользователь создан
        self.assertEqual(User.objects.count(), users_count + 1)
