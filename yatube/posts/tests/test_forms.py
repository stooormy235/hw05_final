from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from ..models import Post, Group, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create(
            username='post_author',
        )
        cls.comm_author = User.objects.create(
            username='comm_author')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test_slug',
            description='Тестовое описание группы',
        )
        cls.post = Post.objects.create(
            text='Текст поста для редактирования',
            author=cls.post_author,
            group=cls.group,
        )
        cls.POST_EDIT_REVERSE = reverse("posts:edit", args=[cls.post.id])
        cls.PROFILE_REVERSE = reverse('posts:profile',
                                      kwargs={'username':
                                              cls.post_author.username})
        cls.CREATE_REVERSE = reverse('posts:create')
        cls.SMALL_GIF = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    def setUp(self):
        cache.clear()
        self.guest_user = Client()
        self.authorized_user = Client()
        self.auth_user_comm = Client()
        self.authorized_user.force_login(self.post_author)
        self.auth_user_comm.force_login(self.comm_author)

    def test_authorized_user_create_post(self):
        """Проверка создания записи авторизированным клиентом."""
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Текст поста',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_user.post(
            self.CREATE_REVERSE,
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            self.PROFILE_REVERSE
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.latest('id')
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post_author)
        self.assertEqual(post.group_id, form_data['group'])
        self.assertIn('image', form_data)

    def test_authorized_user_edit_post(self):
        """Проверка редактирования записи авторизированным клиентом."""
        post = self.post
        uploaded = SimpleUploadedFile(
            name='small_edit.gif',
            content=self.SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Отредактированный текст поста',
            'group': self.group.id,
            'image': uploaded
        }
        response = self.authorized_user.post(
            self.POST_EDIT_REVERSE,
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        post = Post.objects.latest('id')
        self.assertTrue(post.text == form_data['text'])
        self.assertTrue(post.author == self.post_author)
        self.assertTrue(post.group_id == form_data['group'])
        self.assertIn('image', form_data)

    def test_nonauthorized_user_create_post(self):
        """Проверка создания записи не авторизированным пользователем."""
        posts_count = Post.objects.count()
        form_data = {'text': 'Текст поста', 'group': self.group.id}
        response = self.guest_user.post(
            reverse('posts:create'), data=form_data, follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), posts_count)
