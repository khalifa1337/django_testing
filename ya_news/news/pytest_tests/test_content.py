from django.conf import settings
from pytest_django.asserts import assertFormError

from news.forms import CommentForm


def test_news_list_on_page_count(many_news, client, home_url):
    """Проверка количества отображаемых новостей на главной."""
    response = client.get(home_url)
    assert 'object_list' in response.context
    news_count = response.context['object_list'].count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_list_on_page_sorted(many_news, client, home_url):
    """Проверка сортировки новостей на главной странице."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comment_list_on_news_page_sorted(client, news, detail_url):
    """Проверка сортировки комментариев на странице новости."""
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


def test_anonymous_client_has_no_form(news, client, detail_url):
    """Проверка, что анонимный пользователь не видет форму комментариев."""
    response = client.get(detail_url)
    assert 'form' not in response.context


def test_authorized_client_has_form(news, author_client, detail_url):
    """Проверка наличия формы комментария у авторизованного пользователя."""
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
