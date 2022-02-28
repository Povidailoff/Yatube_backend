from http import HTTPStatus

from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..views import PST_PER_PG
from ..models import Post, Group, Follow
from .utils import PostsSetup

User = get_user_model()


class PostsViewsTests(PostsSetup):
    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    page_names = {
        reverse('posts:index'): 'posts/index.html',
        reverse('posts:group_posts', kwargs={'slug': 'test-slug'}):
        'posts/group_list.html',
        reverse('posts:profile', kwargs={'username': 'TestUser'}):
        'posts/profile.html',
        reverse('posts:post_detail', kwargs={'post_id': 1}):
        'posts/post_detail.html',
        reverse('posts:post_create'): 'posts/create_post.html',
        reverse('posts:post_edit', kwargs={'post_id': 1}):
        'posts/create_post.html',
    }

    def test_templates_available(self):
        """Проверка доступности reverse страниц"""
        for reverse_names in self.page_names.keys():
            with self.subTest(reverse_names=reverse_names):
                response = self.authorized_client.get(reverse_names)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_uses_correct_template(self):
        """Проверяем, что используются правильные шаблоны"""
        for reverse_name, template in self.page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_homepage_show_correct_context(self):
        """Шаблон главной страницы использует правильный контекст"""
        # page_obj
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]

        self.assertEqual(first_object.text, 'Тестовая пост для теста тестов')
        self.assertEqual(first_object.group, self.group)
        self.assertEqual(first_object.image, self.post.image)

    def test_group_posts_page_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        # page_obj, group
        response = self.authorized_client.get(reverse(
            'posts:group_posts', kwargs={'slug': 'test-slug'})
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Тестовая пост для теста тестов')
        self.assertEqual(first_object.group, self.group)
        self.assertEqual(response.context['group'], self.group)
        self.assertEqual(first_object.image, self.post.image)

    def test_profile_page_show_correct_context(self):
        """Шаблон профиля имеет правильный контекст"""
        # page_obj, author
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'TestUser'})
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Тестовая пост для теста тестов')
        self.assertEqual(first_object.group, self.group)
        self.assertEqual(response.context['author'], self.user)
        self.assertEqual(first_object.image, self.post.image)

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': 1}))
        )
        self.assertEqual(response.context.get(
            'post').text, 'Тестовая пост для теста тестов'
        )
        self.assertEqual(response.context.get(
            'post').group, self.group
        )
        self.assertEqual(response.context.get('how_much_posts'), 1)
        self.assertEqual(response.context.get('post').image, self.post.image)

    def test_create_post_correct_context(self):
        """Шаблон создания поста имеет правильный контекст"""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        response = self.authorized_client.get(reverse('posts:post_create'))
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_correct_context(self):
        """Шаблон редактирования поста имеет правильный контекст"""
        # post,form,is_edit
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': 1})
        )
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertTrue(response.context.get('is_edit'), True)
        self.assertEqual(response.context.get('post').id, 1)

    def test_post_appears_correct(self):
        """Пост появляется везде, где нужно"""
        response = self.authorized_client.get(reverse('posts:index'))
        # Проверяем, что срез первого объекта соответствует
        self.assertEqual(response.context['page_obj'][0].text[:8], 'Тестовая')
        response = self.authorized_client.get(reverse(
            'posts:group_posts', kwargs={'slug': 'test-slug'}
        ))
        # Проверяем, что срез первого объекта соответствует
        self.assertEqual(response.context['page_obj'][0].text[:8], 'Тестовая')
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'TestUser'}
        ))
        # Проверяем, что срез первого объекта соответствует
        self.assertEqual(response.context['page_obj'][0].text[:8], 'Тестовая')

    def test_comments_appears_correct(self):
        '''Комментарии появляются корректно'''

        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.authorized_client.post(reverse(
            'posts:add_comment',
            kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.context.get(
            'comments')[0].text, 'Тестовый комментарий'
        )

    def test_cache_index_page(self):
        """Тестирование использование кеширования"""
        cache.clear()
        post = Post.objects.create(text='Текстик', author=self.user)
        response = self.client.get(reverse('posts:index'))
        cache_save = response.content
        post.delete()
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(response.content, cache_save)
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, cache_save)

    def test_following_system(self):
        '''Тестируем, что пользователь может
           подписываться на авторов
        '''
        User.objects.create_user('Author')
        self.authorized_client.post(
            reverse('posts:profile_follow', kwargs={'username': 'Author'})
        )
        self.assertEqual(Follow.objects.count(), 1)

    def test_unfollowing_system(self):
        '''Тестируем, что пользователь может
           отписываться от авторов
        '''
        Author = User.objects.create_user('Author')
        Follow.objects.create(
            user=self.user,
            author=Author
        )
        self.authorized_client.post(
            reverse('posts:profile_unfollow', kwargs={'username': 'Author'})
        )
        self.assertEqual(Follow.objects.count(), 0)

    def test_follow_follower_page(self):
        '''Тестируем корректность появления
           постов для подписчиков
        '''
        Author = User.objects.create_user('Author')
        Post.objects.create(
            author=Author,
            text='Текстовый текст'
        )
        Follow.objects.create(
            user=self.user,
            author=Author
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response.context['page_obj']), 1)

    def test_follow_unfollower_page(self):
        '''Тестируется, что посты не появляются в ленте без подписки'''
        Author = User.objects.create_user('Author')
        Post.objects.create(
            author=Author,
            text='Текстовый текст'
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response.context['page_obj']), 0)
        Follow.objects.create(
            user=self.user,
            author=Author
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.user2 = User.objects.create_user(username='TestUser2')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.group2 = Group.objects.create(
            title='Тестовый заголовок2',
            slug='test-slug2',
            description='Тестовое описание2'
        )
        for _ in range(0, 13):
            Post.objects.create(
                author=cls.user,
                text='Тестовая пост для теста тестов',
                group=cls.group,
            )

    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    pages_with_paginator = {
        reverse('posts:index'): 'posts/index.html',
        reverse('posts:group_posts', kwargs={'slug': 'test-slug'}):
        'posts/group_list.html',
        reverse('posts:profile', kwargs={'username': 'TestUser'}):
        'posts/profile.html',
    }

    def test_first_page_contains_ten_records(self):
        """Тестируем первую страницу паджинатора"""
        for view in self.pages_with_paginator.keys():
            with self.subTest(view=view):
                response = self.authorized_client.get(view)
                self.assertEqual(len(response.context['page_obj']), PST_PER_PG)

    def test_second_page_contains_three_records(self):
        """Тестируем оставшиеся посты"""
        for view in self.pages_with_paginator.keys():
            with self.subTest(view=view):
                response = self.authorized_client.get(view + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)

    # Дополнительные проверки
    def test_posts_change_group(self):
        '''Проверяем, что после смены группы записи
           она не отображается в меняемой группе
           и отображается в смененной, затем
           возвращаем как было.
        '''
        post_for_change = Post.objects.get(id=1)
        post_for_change.group = self.group2
        post_for_change.save()
        response = self.authorized_client.get(reverse(
            'posts:group_posts', kwargs={'slug': 'test-slug2'})
        )
        response2 = self.authorized_client.get(reverse(
            'posts:group_posts', kwargs={'slug': 'test-slug'}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 1)
        self.assertEqual(len(response2.context['page_obj']), 2)
        post_for_change.group = self.group
        post_for_change.save()
