from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_lazyfixture import lazy_fixture


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    """Проверка доступности страниц неавторизованному пользователю."""
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_news_pages_availability_for_anonymous_user(client, detail_url):
    """Проверка доступности страницы новости неавторизованному пользователю."""
    response = client.get(detail_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_news_delete_or_edit_availability_for_different_users(
        parametrized_client, name, comment_id_for_args, expected_status
):
    """
    Проверка доступности страниц редактирования и удаления
    для разных пользователей.
    """
    url = reverse(name, args=comment_id_for_args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', lazy_fixture('comment_id_for_args')),
        ('news:delete', lazy_fixture('comment_id_for_args')),
    ),
)
def test_redirects(client, name, args):
    """Проверка редиректа для анонимного пользователя."""
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == expected_url
