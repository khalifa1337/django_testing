from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse

from news.models import Comment, News


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture
def anonymous_client():
    return Client()


@pytest.fixture
def author(django_user_model):
    """Фикстура для создания автора."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Фикстура для создания другого пользователя.."""
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """Фикстура для создания клиента для автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Фикстура для создания клиента для другого пользователя."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    """Фикстура для создания новости."""
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )


@pytest.fixture
def comment(author, news):
    """Фикстура для создания комментария."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='А вот в наше время было лучше!',
    )


@pytest.fixture
def many_news():
    """Фикстура для создания нескольких новостей."""
    today = datetime.today()
    News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def many_comments(news, author):
    """Фикстура для создания нескольких комментариев."""
    today = datetime.today()
    Comment.objects.bulk_create(
        Comment(
            news=news.id,
            author=author,
            text=f'Комментарий {index}',
            date=today - timedelta(days=index)
        )
        for index in range(5)
    )


@pytest.fixture
def detail_url(news):
    """Фикстура для получения url новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def home_url():
    """Фикстура для получения url главной страницы."""
    return reverse('news:home')


@pytest.fixture
def comment_delete_url(comment):
    """Фикстура для получения url удаления комментария."""
    return reverse('news:delete', args=(comment.id, ))


@pytest.fixture
def comment_edit_url(comment):
    """Фикстура для получения url редактирования комментария."""
    return reverse('news:edit', args=(comment.id, ))


@pytest.fixture
def login_url():
    """Фикстура для получения url логина."""
    return reverse('users:login')
