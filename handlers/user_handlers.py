from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from services.rag_client import RAGClient
from config import RAG_API_URL

router = Router()
rag_client = RAGClient(RAG_API_URL)

class SearchStates(StatesGroup):
    waiting_for_query = State()
    waiting_for_author = State()
    waiting_for_date = State()
    waiting_for_topic = State()

def make_filter_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Выполнить поиск")],
            [KeyboardButton(text="👤 Автор"), KeyboardButton(text="📅 Дата")],
            [KeyboardButton(text="🔖 Тема")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Привет! Я бот для поиска технических новостей.\n"
        "Введите ваш запрос или нажмите /search."
    )

@router.message(F.text == "/help")
async def process_help_command(message: Message):
    await message.answer(
        'Запросите через /search название '
        'интересующей вас статьи или воспользуйтесь кнопками '
        'под диалоговой строкой для более тонкой '
        'настройки.\n'
        'Поиск осуществляется с помощью RAG-агента, '
        'настроенного на российские интернет-ресурсы'
    )

@router.message(F.text == "/search")
async def cmd_search(message: Message, state: FSMContext):
    await state.set_state(SearchStates.waiting_for_query)
    await message.answer("Введите поисковый запрос:")

@router.message(SearchStates.waiting_for_query)
async def process_query(message: Message, state: FSMContext):
    await state.update_data(query=message.text, author=None, date=None, topic=None)
    await state.set_state(None)  # временно выйдем из состояния
    await message.answer("Выберите фильтры (или нажмите ✅ Выполнить поиск):", reply_markup=make_filter_keyboard())

# Обработка кнопок фильтров
@router.message(F.text == "👤 Автор")
async def filter_author(message: Message, state: FSMContext):
    await state.set_state(SearchStates.waiting_for_author)
    await message.answer("Введите автора:")

@router.message(SearchStates.waiting_for_author)
async def process_author(message: Message, state: FSMContext):
    await state.update_data(author=message.text)
    await state.set_state(None)
    await message.answer("Фильтр по автору установлен.", reply_markup=make_filter_keyboard())

@router.message(F.text == "📅 Дата")
async def filter_date(message: Message, state: FSMContext):
    await state.set_state(SearchStates.waiting_for_date)
    await message.answer("Введите дату (ГГГГ-ММ-ДД):")

@router.message(SearchStates.waiting_for_date)
async def process_date(message: Message, state: FSMContext):
    await state.update_data(date=message.text)
    await state.set_state(None)
    await message.answer("Фильтр по дате установлен.", reply_markup=make_filter_keyboard())

@router.message(F.text == "🔖 Тема")
async def filter_topic(message: Message, state: FSMContext):
    await state.set_state(SearchStates.waiting_for_topic)
    await message.answer("Введите тему (например: ИИ, дроны, финтех):")

@router.message(SearchStates.waiting_for_topic)
async def process_topic(message: Message, state: FSMContext):
    await state.update_data(topic=message.text)
    await state.set_state(None)
    await message.answer("Фильтр по теме установлен.", reply_markup=make_filter_keyboard())

@router.message(F.text == "✅ Выполнить поиск")
async def run_search(message: Message, state: FSMContext):
    data = await state.get_data()
    query = data.get("query")
    if not query:
        await message.answer("Сначала введите запрос через /search.")
        return

    try:
        results = await rag_client.search(
            query=query,
            author=data.get("author"),
            date=data.get("date"),
            topic=data.get("topic")
        )
    except Exception as e:
        await message.answer("❌ Ошибка при поиске. Попробуйте позже.")
        return

    articles = results.get("articles", [])
    if not articles:
        await message.answer("Ничего не найдено.")
        return

    summary = results.get("summary", "Результаты поиска")
    text = f"<b>{summary}</b>\n\n"

    for art in articles[:10]:
        title = art.get("title", "Без названия")
        url = art.get("url", "#")
        author = art.get("author", "—")
        date = art.get("date", "—")
        topic = art.get("topic", "—")

        # Экранирование HTML
        from html import escape
        title_esc = escape(title)
        author_esc = escape(author)
        date_esc = escape(date)
        topic_esc = escape(topic)

        text += (
            f"• <a href='{url}'>{title_esc}</a>\n"
            f"  Автор: {author_esc} | Дата: {date_esc} | Тема: {topic_esc}\n\n"
        )

    # Telegram ограничивает длину сообщения (~4096 символов)
    if len(text) > 4000:
        text = text[:4000] + "... (результат усечён)"

    await message.answer(text, parse_mode="HTML", disable_web_page_preview=False)