from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture


ANONYMOUS_CLIENT = lazy_fixture('anonymous_client')
AUTHOR_CLIENT = lazy_fixture('author_client')
NOT_AUTHOR_CLIENT = lazy_fixture('not_author_client')
HOME_URL = lazy_fixture('home_url')
LOGIN_URL = lazy_fixture('login_url')
LOGOUT_URL = lazy_fixture('logout_url')
SIGNUP_URL = lazy_fixture('signup_url')
DETAIL_URL = lazy_fixture('detail_url')
EDIT_URL = lazy_fixture('comment_edit_url')
DELETE_URL = lazy_fixture('comment_delete_url')


@pytest.mark.parametrize(
    'url, client, expected_status',
    (
        (HOME_URL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (LOGIN_URL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (LOGOUT_URL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (SIGNUP_URL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (DETAIL_URL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (EDIT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (DELETE_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (EDIT_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (DELETE_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
    )
)
def test_page_status_availability(client, url, expected_status):
    """Проверка статус кодов доступных страниц для разных пользователей."""
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url, client',
    (
        (EDIT_URL, ANONYMOUS_CLIENT),
        (DELETE_URL, ANONYMOUS_CLIENT),
    ),
)
def test_redirects(client, url, login_url):
    """Проверка редиректа для анонимного пользователя."""
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
