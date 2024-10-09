from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_lazyfixture import lazy_fixture

COMMENT_FOR_ARGS = lazy_fixture('comment')
NEWS_FOR_ARGS = lazy_fixture('news')
ANONYMOUS_CLIENT = lazy_fixture('anonymous_client')
AUTHOR_CLIENT = lazy_fixture('author_client')
NOT_AUTHOR_CLIENT = lazy_fixture('not_author_client')


@pytest.mark.parametrize(
    'name, args, client, expected_status',
    (
        ('news:home', None, ANONYMOUS_CLIENT, HTTPStatus.OK),
        ('users:login', None, ANONYMOUS_CLIENT, HTTPStatus.OK),
        ('users:logout', None, ANONYMOUS_CLIENT, HTTPStatus.OK),
        ('users:signup', None, ANONYMOUS_CLIENT, HTTPStatus.OK),
        ('news:detail', NEWS_FOR_ARGS, ANONYMOUS_CLIENT, HTTPStatus.OK),
        ('news:edit', COMMENT_FOR_ARGS, AUTHOR_CLIENT, HTTPStatus.OK),
        ('news:delete', COMMENT_FOR_ARGS, AUTHOR_CLIENT, HTTPStatus.OK),
        ('news:edit',
         COMMENT_FOR_ARGS,
         NOT_AUTHOR_CLIENT,
         HTTPStatus.NOT_FOUND
         ),
        ('news:delete',
         COMMENT_FOR_ARGS,
         NOT_AUTHOR_CLIENT,
         HTTPStatus.NOT_FOUND
         ),
    )
)
def test_page_status_availability(client, args, name, expected_status):
    """Проверка статус кодов доступных страниц для разных пользователей."""
    if args:
        args = (args.id, )
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, client',
    (
        ('news:edit', ANONYMOUS_CLIENT),
        ('news:delete', ANONYMOUS_CLIENT),
    ),
)
def test_redirects(client, name, login_url, comment):
    """Проверка редиректа для анонимного пользователя."""
    url = reverse(name, args=(comment.id, ))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == expected_url
