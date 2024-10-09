from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse

from news.models import Comment, News


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
def news(db):
    """Фикстура для создания новости."""
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news


@pytest.fixture
def comment(author, news):
    """Фикстура для создания комментария."""
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='А вот в наше время было лучше!',
    )
    return comment


@pytest.fixture
def comment_id_for_args(comment):
    """Фикстура для получения id комментария в аргументах."""
    return (comment.id,)


@pytest.fixture
def news_id_for_args(news):
    """Фикстура для получения id новости в аргументах."""
    return (news.id,)

@pytest.fixture
def form_data():
    """Фикстура для создания словаря с данными для формы комментария."""
    return {
        'text': 'Новый текст',
    }


@pytest.fixture
def many_news(db):
    """Фикстура для создания нескольких новостей."""
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    many_news = News.objects.bulk_create(all_news)
    return many_news


@pytest.fixture
def detail_url(news):
    """Фикстура для получения url новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def home_url():
    """Фикстура для получения url главной страницы."""
    return reverse('news:home')


@pytest.fixture
def comment_delete_url(comment_id_for_args):
    """Фикстура для получения url удаления комментария."""
    return reverse('news:delete', args=comment_id_for_args)


@pytest.fixture
def comment_edit_url(comment_id_for_args):
    """Фикстура для получения url редактирования комментария."""
    return reverse('news:edit', args=comment_id_for_args)


@pytest.fixture
def login_url():
    return reverse('users:login')
