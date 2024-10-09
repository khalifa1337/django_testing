from http import HTTPStatus

from django.test import Client
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.test_utils import BaseTestCaseWithNote, NoteCreationForm


class TestNoteCreation(NoteCreationForm):
    """
    Тестирование логики создания заметок.
    Наследуется от класса NoteCreationForm, который содержит в себе:
    Пользователь self.author
    Пользователь self.reader
    Содержит в себе:
    Авторизованный клиент self.auth_client от self.author
    URL для создания заметки self.create_url
    Данные для создания заметки self.form_data
    """
    def test_users_can_or_cant_create_note(self):
        """
        Проверка невозможности создания заметки не пользователем,
        и проверка возможности создания заметки пользователем.
        Возможно, с точки зрения логики стоит разделить на отдельные,
        но с точки зрения повтора кода - так более эффективно.
        """
        users_nots = (
            (self.client, 0),
            (self.auth_client, 1),
        )
        for user, notes_count in users_nots:
            with self.subTest(user=user):
                initial_count = Note.objects.count()
                user.post(self.create_url, data=self.form_data)
                self.assertEqual(
                    Note.objects.count(),
                    initial_count + notes_count
                )
                if user == self.auth_client:
                    our_note = Note.objects.get()
                    self.assertEqual(our_note.title, self.form_data['title'])
                    self.assertEqual(our_note.text, self.form_data['text'])
                    self.assertEqual(our_note.slug, self.form_data['slug'])
                    self.assertEqual(our_note.author, self.author)

    def test_slug_field_auto_generated(self):
        """
        Проверка того, что slug будет верно сгенерирован в случае,
        если он не передаётся явно.
        """
        self.form_data.pop('slug')
        self.auth_client.post(self.create_url, data=self.form_data)
        new_slug = slugify(self.form_data['title'])
        self.assertEqual(Note.objects.get().slug, new_slug)


class TestNoteCreationValidate(BaseTestCaseWithNote, NoteCreationForm):
    """
    Тестирование логики валидации данных для создания заметки.
    Наследуется от класса NoteCreationForm, который содержит в себе:
    Пользователь self.author
    Пользователь self.reader
    Содержит в себе:
    Авторизованный клиент self.auth_client от self.author
    URL для создания заметки self.create_url
    Данные для создания заметки self.form_data
    Также от класса BaseTestCaseWithNote, который содержит в себе:
    Заметка self.note

    p.s. По сути, в рамках наследования идет несколько отсылок на один класс,
    как я понимаю, явных ошибок это не вызывает.
    """
    def test_users_cant_add_note_with_same_slug(self):
        """Проверка невозможности создания заметки с одинаковым slug."""
        self.form_data['slug'] = 'test-slug'
        response = self.auth_client.post(self.create_url, data=self.form_data)
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)


class TestCommentEditDelete(BaseTestCaseWithNote, NoteCreationForm):
    """
    Тестирование логики работы с комментариями.
    Наследуется от класса NoteCreationForm, который содержит в себе:
    Пользователь self.author
    Пользователь self.reader
    Содержит в себе:
    Авторизованный клиент self.auth_client от self.author
    URL для создания заметки self.create_url
    Данные для создания заметки self.form_data
    Также от класса BaseTestCaseWithNote, который содержит в себе:
    Заметка self.note
    """
    NEW_NOTE_TEXT = 'Продолжаем вести наблюдение.'

    @classmethod
    def setUpTestData(cls):
        """
        Дополнительно создаем клиент другого пользователя,
        Объявляем часто-используемые ссылки,
        Задаем новый текст комментария.
        """
        super().setUpTestData()
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.done_url = reverse('notes:success')
        cls.form_data['text'] = cls.NEW_NOTE_TEXT

    def test_author_can_delete_note(self):
        """Проверка возможности автором удаления своей заметки."""
        response = self.auth_client.delete(self.delete_url)
        self.assertRedirects(response, self.done_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        """Проверка невозможности удаления заметки другого пользователя."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        """Проверка возможности автора редактирования своей заметки."""
        response = self.auth_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.done_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_comment_of_another_user(self):
        """Тест невозможности редактирования заметки другого пользователя."""
        note_text = self.note.text
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, note_text)
