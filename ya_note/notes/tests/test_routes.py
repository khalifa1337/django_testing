from http import HTTPStatus

from notes.tests.test_utils import (ADD_URL, DELETE_URL, DETAIL_URL, EDIT_URL,
                                    HOME_URL, LIST_URL, LOGIN_URL, LOGOUT_URL,
                                    SIGNUP_URL, SUCCESS_URL,
                                    BaseTestCaseWithNote)


class TestRoutes(BaseTestCaseWithNote):
    """
    Тестирование доступности страниц.
    Наследуется от класса, который содержит в себе:
    Пользователь cls.author и клиент cls.author_client
    Пользователь cls.reader и клиент cls.reader_client
    Заметка cls.note
    """
    def test_pages_availability(self):
        """Проверка доступности страниц для различных типов пользователей."""
        status_ok = HTTPStatus.OK
        status_404 = HTTPStatus.NOT_FOUND

        pages = (
            (HOME_URL, self.anonymous_client, status_ok),
            (LOGIN_URL, self.anonymous_client, status_ok),
            (SIGNUP_URL, self.anonymous_client, status_ok),
            (LOGOUT_URL, self.anonymous_client, status_ok),
            (LIST_URL, self.reader_client, status_ok),
            (ADD_URL, self.reader_client, status_ok),
            (SUCCESS_URL, self.reader_client, status_ok),
            (DETAIL_URL, self.author_client, status_ok),
            (EDIT_URL, self.author_client, status_ok),
            (DELETE_URL, self.author_client, status_ok),
            (DETAIL_URL, self.reader_client, status_404),
            (EDIT_URL, self.reader_client, status_404),
            (DELETE_URL, self.reader_client, status_404),
        )

        for url, user, expected_status in pages:
            with self.subTest(page=url, expected_status=expected_status):
                response = user.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirect_for_anonymous_client(self):
        """Проверка редиректа для анонимного пользователя."""
        pages = (
            LIST_URL,
            DETAIL_URL,
            EDIT_URL,
            DELETE_URL,
            ADD_URL,
            SUCCESS_URL,
        )

        for url in pages:
            with self.subTest(name=url):
                redirect_url = f'{LOGIN_URL}?next={url}'
                response = self.anonymous_client.get(url)
                self.assertRedirects(response, redirect_url)
