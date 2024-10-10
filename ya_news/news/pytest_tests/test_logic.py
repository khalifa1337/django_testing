from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

FORM_DATA = {'text': 'Новый текст', }


def test_anonymous_user_cant_create_comment(client, detail_url, login_url):
    """Проверка невозможности создания комментария без авторизации."""
    response = client.post(detail_url, data=FORM_DATA)
    previous_comments_count = Comment.objects.count()
    expected_url = f'{login_url}?next={detail_url}'
    assertRedirects(response, expected_url)
    assert response.url == expected_url
    assert Comment.objects.count() == previous_comments_count


def test_auth_user_can_create_comment(
    author_client, author, detail_url
):
    """Проверка возможности создания коммента авторизованным пользователем."""
    previous_comment_count = Comment.objects.count()
    response = author_client.post(detail_url, data=FORM_DATA)
    success_url = detail_url + '#comments'
    assertRedirects(response, success_url)
    assert Comment.objects.count() == previous_comment_count + 1
    our_comment = Comment.objects.get()
    assert our_comment.text == FORM_DATA['text']
    assert our_comment.author == author


@pytest.mark.parametrize('bad_word', BAD_WORDS)
def test_form_with_badwords_dont_posted_to_db(
    author_client, bad_word, detail_url
):
    """
    Проверка, что форма не создается, если комментарий содержит
    недопустимые слова.
    """
    previous_comment_count = Comment.objects.count()
    bad_words_data = {'text': f'Я сказал {bad_word}, что ты мне сделаешь?'}
    response = author_client.post(detail_url, data=bad_words_data)
    assert 'form' in response.context
    assertFormError(response, 'form', 'text', WARNING)
    comments_count = Comment.objects.count()
    assert comments_count == previous_comment_count


def test_author_can_edit_comment(
    author_client, comment, detail_url, comment_edit_url
):
    """Проверка возможности редактирования своего комментария."""
    response = author_client.post(comment_edit_url, FORM_DATA)
    success_url = detail_url + '#comments'
    assertRedirects(response, success_url)
    comment = Comment.objects.get(id=comment.id)
    assert comment.text == FORM_DATA['text']


def test_author_can_delete_comment(
    author_client, comment_delete_url, detail_url, comment
):
    """Проверка возможности удаления своего комментария."""
    previous_comment_count = Comment.objects.count()
    response = author_client.post(comment_delete_url)
    success_url = detail_url + '#comments'
    assertRedirects(response, success_url)
    assert Comment.objects.count() == previous_comment_count - 1
    assert not Comment.objects.filter(id=comment.id).exists()


def test_other_user_cant_edit_comment(
    not_author_client, comment, comment_edit_url
):
    """Тест невозможности редактирования комментария другого пользователя."""
    original_comment = comment.text
    response = not_author_client.post(comment_edit_url, FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment = Comment.objects.get(id=comment.id)
    assert comment.text == original_comment


def test_other_user_cant_delete_comment(
    not_author_client, comment_delete_url, comment
):
    """Тест невозможности удаления комментария другого пользователя."""
    previous_comment_count = Comment.objects.count()
    previous_comment = Comment.objects.get(id=comment.id)
    response = not_author_client.post(comment_delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    current_comment = Comment.objects.get(id=comment.id)
    assert current_comment.text == previous_comment.text
    assert Comment.objects.count() == previous_comment_count
