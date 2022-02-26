from django.contrib.auth import get_user_model

from .utils import PostsSetup

User = get_user_model()


class PostModelTest(PostsSetup):
    def test_post_have_correct_object_names(self):
        """Проверяем, что у постов корректно работает __str__."""
        post = self.post
        piecetext = 15
        self.assertEqual(str(post), post.text[:piecetext])

    def test_group_have_correct_object_names(self):
        """Проверяем, что у групп корректно работает __str__."""
        group = self.group
        self.assertEqual(str(group), group.title)
