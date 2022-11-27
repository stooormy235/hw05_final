from django.test import TestCase
from django.conf import settings

from ..models import Post, Group, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            text='Тестовый текст больше 15 символов для проверки...',
            author=cls.user,
        )

    def test_post_str(self):
        """Проверка __str__ у post."""
        self.assertEqual(self.post.text[:settings.MAX_TYPE], str(self.post))


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_group_str(self):
        """Проверка __str__ у group."""
        self.assertEqual(self.group.title, str(self.group))
