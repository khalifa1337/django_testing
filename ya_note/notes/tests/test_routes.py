from http import HTTPStatus

from django.urls import reverse

from notes.tests.test_utils import BaseTestCaseWithNote


class TestRoutes(BaseTestCaseWithNote):
    """
    Тестирование доступности страниц.
    Наследуется от класса, который содержит в себе:
    Пользователь cls.author
    Пользователь cls.reader
    Заметка cls.note
    """

    def test_pages_for_all_users_availability(self):
        """Проверка доступности страниц для всех пользователей."""
        pages = (
            ('notes:home', None),
            ('users:login', None),
            ('users:signup', None),
            ('users:logout', None),
        )

        for page, args in pages:
            with self.subTest(page=page):
                url = reverse(page, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_for_auth_user_availability(self):
        """Проверка доступности страниц для авторизированных пользователей."""
        pages = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:success', None),
        )

        for page, args in pages:
            with self.subTest(page=page):
                self.client.force_login(self.reader)
                url = reverse(page, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_only_for_author_availability(self):
        """Проверка доступности страниц только для их автора."""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )

        pages = (
            'notes:detail',
            'notes:edit',
            'notes:delete',
        )

        for user, status in users_statuses:
            self.client.force_login(user)
            for name in pages:
                with self.subTest(name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Проверка редиректа для анонимного пользователя."""
        login_url = reverse('users:login')

        pages = (
            ('notes:list', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:add', None),
            ('notes:success', None),
        )

        for name, args in pages:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
