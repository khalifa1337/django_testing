from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

DEFAULT_SLUG = 'test-slug'
EDIT_URL = reverse('notes:edit', args=(DEFAULT_SLUG,))
DELETE_URL = reverse('notes:delete', args=(DEFAULT_SLUG,))
DONE_URL = reverse('notes:success')
LOGIN_URL = reverse('users:login')
LIST_URL = reverse('notes:list')


class BaseTestCaseWithoutNote(TestCase):
    """
    Так как для нескольких тестов используются одинаковые пользователи,
    то, с точки зрения подхода DRY, более подходящим будет вынести их в
    отдельный класс, по аналогии с фикстурами.
    Содержит двух готовых пользователей:
    cls.author
    cls.reader

    p.s. Как я понимаю, явно задавать их абстрактными нет необходимости,
    так как при тестировании их явные объекты не создаются.
    """
    @classmethod
    def setUpTestData(cls):
        """Создание зетки и пользователей для тестирования."""
        cls.author = User.objects.create_user(
            username='IAmAuthorTrustMe',
        )
        cls.reader = User.objects.create_user(
            username='IAmReaderDontTrustMe',
        )


class BaseTestCaseWithNote(BaseTestCaseWithoutNote):
    """
    Так как часть тестов использует одинаковую заметку, то может
    быть удобнее использовать ее из отдельного класса.
    Наследуется от класса (BaseTestCaseWithoutNote), который содержит в себе:
    Пользователь cls.author
    Пользователь cls.reader

    Содержит в себе заметку cls.note
    """
    @classmethod
    def setUpTestData(cls):
        """Создание земетки."""
        super().setUpTestData()
        cls.note = Note.objects.create(
            title='Тестовый заголовок',
            text='Тестовая заметка',
            slug=DEFAULT_SLUG,
            author=cls.author,
        )


class NoteCreationForm(BaseTestCaseWithoutNote):
    """
    Класс для удобства тестирования в тестах, требующих отправки формы.
    Наследуется от класса (BaseTestCaseWithoutNote), который содержит в себе:
    Пользователь cls.author
    Пользователь cls.reader
    Содержит в себе:
    Авторизовынный клиент cls.auth_client от cls.author
    URL для создания заметки cls.create_url
    Данные для создания заметки cls.form_data
    """
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.create_url = reverse('notes:add')
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'test-create-slug'
        }
