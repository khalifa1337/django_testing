from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note
from notes.tests.test_utils import (LIST_URL, BaseTestCaseWithNote,
                                    BaseTestCaseWithoutNote)


class TestListPage(BaseTestCaseWithoutNote):
    """
    Тестирование страницы списка заметок.
    Наследуется от BaseTestCaseWithoutNote, который содержит в себе:
    Пользователь cls.author
    Пользователь cls.reader
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        """Создание нескольких дополнительных заметок."""
        all_notes = [
            Note(
                title=f'Заметка № {index}',
                text='Почему именно 42?!.',
                author=author,
                slug=f'{author.id}-{index}',
            )
            for index in range(3)
            for author in [cls.author, cls.reader]
        ]
        Note.objects.bulk_create(all_notes)

    def test_only_authors_can_see_notes(self):
        """Проверка, что на странице отображаются только заметки автора."""
        self.client.force_login(self.author)
        response = self.client.get(LIST_URL)
        # Также в тесте проверяем, что в object_list присутствуют заметки.
        self.assertIn('object_list', response.context)
        notes = response.context['object_list']
        self.assertEqual(len(notes), 3)
        author = [note.author for note in notes]
        self.assertEqual(set(author), {self.author})
        reader_notes_exist = any(note.author == self.reader for note in notes)
        self.assertFalse(
            reader_notes_exist,
            "На странице отображаются заметки другого пользователя"
        )


class TestDetailPage(BaseTestCaseWithNote):
    """Тестирование страницы отдельной заметки."""
    def test_authorized_client_has_form(self):
        """Проверка формы для авторизированных пользователей."""
        pages = (
            ('notes:edit', (self.note.slug,)),
            ('notes:add', None),
        )
        self.client.force_login(self.author)
        for name, args in pages:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIsInstance(response.context.get('form'), NoteForm)
