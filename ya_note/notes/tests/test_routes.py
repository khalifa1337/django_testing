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
    def test_pages_availability(self):
        """Проверка доступности страниц для различных типов пользователей."""
        status_ok = HTTPStatus.OK
        status_404 = HTTPStatus.NOT_FOUND
        pages = (
            ('notes:home', None, None, status_ok),
            ('users:login', None, None, status_ok),
            ('users:signup', None, None, status_ok),
            ('users:logout', None, None, status_ok),
            ('notes:list', None, self.reader, status_ok),
            ('notes:add', None, self.reader, status_ok),
            ('notes:success', None, self.reader, status_ok),
            ('notes:detail', (self.note.slug,), self.author, status_ok),
            ('notes:edit', (self.note.slug,), self.author, status_ok),
            ('notes:delete', (self.note.slug,), self.author, status_ok),
            ('notes:detail', (self.note.slug,), self.reader, status_404),
            ('notes:edit', (self.note.slug,), self.reader, status_404),
            ('notes:delete', (self.note.slug,), self.reader, status_404),
        )
        for page, args, user, expected_status in pages:
            if user:
                self.client.force_login(user)
            with self.subTest(page=page, expected_status=expected_status):
                url = reverse(page, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, expected_status)

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
