from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Post, Comment
from .utils import PostsSetup

User = get_user_model()


class PostFormsTests(PostsSetup):
    def setUp(self) -> None:
        super().setUp()
        # Авторизованный автор поста
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текстик',
            'author': self.user,
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user}
        ))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись с заданным текстом
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текстик',
            ).exists()
        )

    def test_users_can_edit_posts(self):
        """Проверка, что посты редактируются"""
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Тестовый текст',
            'author': self.user,
        }

        response = self.authorized_client.post(reverse(
            'posts:post_edit',
            kwargs={'post_id': 1}),
            data=form_data,
            follow=True
        )
        # Сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id})
        )
        # Проверяем, что общее количетсво записей не изменилось
        self.assertEqual(Post.objects.count(), posts_count)
        # Запись изменилась
        self.assertEqual(
            Post.objects.get(pk=1).text, 'Тестовый текст'
        )

    def test_logged_users_can_add_comment(self):
        '''Тестируем добавление комментариев к посту'''
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        self.authorized_client.post(reverse(
            'posts:add_comment',
            kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)

    def test_anonymous_cant_post_comment(self):
        '''Неавторизованный пользователь не может комментировать'''

        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        self.client.post(reverse(
            'posts:add_comment',
            kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count)
