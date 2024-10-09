from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_lazyfixture import lazy_fixture

COMMENT_ID_FOR_ARGS = lazy_fixture('comment_id_for_args')
NEWS_ID_FOR_ARGS = lazy_fixture('news_id_for_args')
ANONYMOUS_CLIENT = lazy_fixture('anonymous_client')
AUTHOR_CLIENT = lazy_fixture('author_client')
NOT_AUTHOR_CLIENT = lazy_fixture('not_author_client')


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args, client, expected_status',
    (
        # Страницы для неавторизованных пользователей
        ('news:home', None, ANONYMOUS_CLIENT, HTTPStatus.OK),
        ('users:login', None, ANONYMOUS_CLIENT, HTTPStatus.OK),
        ('users:logout', None, ANONYMOUS_CLIENT, HTTPStatus.OK),
        ('users:signup', None, ANONYMOUS_CLIENT, HTTPStatus.OK),
        ('news:detail', NEWS_ID_FOR_ARGS, ANONYMOUS_CLIENT, HTTPStatus.OK),
        # Страницы для авторизованных пользователей
        ('news:edit', COMMENT_ID_FOR_ARGS, AUTHOR_CLIENT, HTTPStatus.OK),
        ('news:delete', COMMENT_ID_FOR_ARGS, AUTHOR_CLIENT, HTTPStatus.OK),
        ('news:edit',
         COMMENT_ID_FOR_ARGS,
         NOT_AUTHOR_CLIENT,
         HTTPStatus.NOT_FOUND
         ),
        ('news:delete',
         COMMENT_ID_FOR_ARGS,
         NOT_AUTHOR_CLIENT,
         HTTPStatus.NOT_FOUND
         ),
    )
)
def test_page_status_availability(client, args, name, expected_status):
    """Проверка статус кодов доступных страниц для разных пользователей."""
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args, client',
    (
        ('news:edit', COMMENT_ID_FOR_ARGS, ANONYMOUS_CLIENT),
        ('news:delete', COMMENT_ID_FOR_ARGS, ANONYMOUS_CLIENT),
    ),
)
def test_redirects(client, name, args, login_url):
    """Проверка редиректа для анонимного пользователя."""
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == expected_url
