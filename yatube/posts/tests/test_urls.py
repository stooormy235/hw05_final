from http import HTTPStatus
from django.test import Client, TestCase
from django.core.cache import cache

from ..models import Post, Group, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='HASNoName')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description="Тестовое описание",
        )
        cls.PUBLIC_URLS = {
            '/',
            f'/group/{cls.group.slug}/',
            f'/profile/{cls.user}/',
            f'/posts/{cls.post.id}/',
        }
        cls.PRIVATE_URLS = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.user.username}/': 'posts/profile.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
            f'/posts/{cls.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)
        cache.clear()

    def test_urls_exists_at_desired_location(self):
        for adress in self.PUBLIC_URLS:
            with self.subTest(adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_availability(self):
        """Проверка доступности приватных страниц"""
        for url, template in self.PRIVATE_URLS.items():
            status_code = self.authorized_client.get(url).status_code
            self.assertEqual(status_code, HTTPStatus.OK)

    def test_page_availability_public_urls(self):
        """Проверка доступности публичных страниц"""
        for url in self.PUBLIC_URLS:
            with self.subTest(url):
                status_code = self.guest_client.get(url).status_code
                self.assertEqual(status_code, HTTPStatus.OK)

    def test_unexisting_page_at_desired_location(self):
        """Проверка несуществующей страницы."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in self.PRIVATE_URLS.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
