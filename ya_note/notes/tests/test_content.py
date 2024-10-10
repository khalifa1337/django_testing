from notes.forms import NoteForm
from notes.models import Note
from notes.tests.test_utils import (ADD_URL, EDIT_URL, LIST_URL,
                                    BaseTestCaseWithNote,
                                    BaseTestCaseWithoutNote)


class TestListPage(BaseTestCaseWithoutNote):
    """
    Тестирование страницы списка заметок.
    Наследуется от BaseTestCaseWithoutNote, который содержит в себе:
    Пользователь cls.author и клиент cls.author_client
    Пользователь cls.reader и клиент cls.reader_client
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
        response = self.author_client.get(LIST_URL)
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
            EDIT_URL,
            ADD_URL,
        )
        for url in pages:
            with self.subTest(name=url):
                response = self.author_client.get(url)
                self.assertIsInstance(response.context.get('form'), NoteForm)
