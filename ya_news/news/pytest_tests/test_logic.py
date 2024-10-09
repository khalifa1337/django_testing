from http import HTTPStatus

import pytest
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

FORM_DATA = {'text': 'Новый текст', }


def test_anonymous_user_cant_create_comment(client, detail_url):
    """Проверка невозможности создания комментария без авторизации."""
    response = client.post(detail_url, data=FORM_DATA)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={detail_url}'
    assert response.status_code == 302
    assert response.url == expected_url
    assert Comment.objects.count() == 0


def test_auth_user_can_create_comment(
    author_client, author, detail_url
):
    """Проверка возможности создания коммента авторизованным пользователем."""
    response = author_client.post(detail_url, data=FORM_DATA)
    success_url = detail_url + '#comments'
    assert response.url == success_url
    assert Comment.objects.count() == 1
    our_comment = Comment.objects.get()
    assert our_comment.text == FORM_DATA['text']
    assert our_comment.author == author


def test_form_with_badwords_dont_posted_to_db(author_client, detail_url):
    """
    Проверка, что форма не создается, если комментарий содержит
    недопустимые слова.
    """
    bad_words_data = {'text': f'Я сказал {BAD_WORDS[0]}, что ты мне сделаешь?'}
    response = author_client.post(detail_url, data=bad_words_data)
    assert 'form' in response.context
    form = response.context['form']
    assert not form.is_valid()
    assert 'text' in form.errors
    assert WARNING in form.errors['text']
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_edit_comment(
    author_client, comment, detail_url, comment_edit_url
):
    """Проверка возможности редактирования своего комментария."""
    response = author_client.post(comment_edit_url, FORM_DATA)
    assert response.status_code == 302
    success_url = detail_url + '#comments'
    assert response.url == success_url
    comment.refresh_from_db()
    assert comment.text == FORM_DATA['text']


def test_author_can_delete_comment(
    author_client, comment_delete_url, detail_url
):
    """Проверка возможности удаления своего комментария."""
    response = author_client.post(comment_delete_url)
    assert response.status_code == 302
    success_url = detail_url + '#comments'
    assert response.url == success_url
    assert Comment.objects.count() == 0


def test_other_user_cant_edit_comment(
    not_author_client, comment, comment_edit_url
):
    """Тест невозможности редактирования комментария другого пользователя."""
    original_comment = comment.text
    response = not_author_client.post(comment_edit_url, FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == original_comment


def test_other_user_cant_delete_comment(not_author_client, comment_delete_url):
    """Тест невозможности удаления комментария другого пользователя."""
    response = not_author_client.post(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
