from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from models.database import Database, UserProfile
from utils.ai_assistant import AIAssistant

router = Router()
db = Database()
ai_assistant = AIAssistant()


class ProfileStates(StatesGroup):
    waiting_for_background = State()
    waiting_for_interests = State()
    waiting_for_skills = State()
    waiting_for_goals = State()


def create_main_menu() -> InlineKeyboardMarkup:
    """Create main menu keyboard"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🤖 Задать вопрос", callback_data="ask_question")],
            [InlineKeyboardButton(text="📊 Сравнить программы", callback_data="compare_programs")],
            [
                InlineKeyboardButton(
                    text="🎯 Получить рекомендацию", callback_data="get_recommendation"
                )
            ],
            [InlineKeyboardButton(text="📚 Гид по поступлению", callback_data="admission_guide")],
            [InlineKeyboardButton(text="👤 Мой профиль", callback_data="user_profile")],
            [InlineKeyboardButton(text="ℹ️ Помощь", callback_data="help")],
        ]
    )
    return keyboard


def create_profile_menu() -> InlineKeyboardMarkup:
    """Create profile management menu"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Настроить профиль", callback_data="setup_profile")],
            [InlineKeyboardButton(text="👀 Посмотреть профиль", callback_data="view_profile")],
            [InlineKeyboardButton(text="🔄 Обновить профиль", callback_data="update_profile")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
        ]
    )
    return keyboard


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command"""
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or "Пользователь"

    # Check if user exists
    existing_profile = db.get_user_profile(user_id)

    welcome_text = f"""
🎓 Добро пожаловать в консультант по магистерским программам ИТМО по ИИ!

Привет, {username}! Я помогу тебе выбрать подходящую программу магистратуры и спланировать обучение.

🔍 **Доступные программы:**
• "Искусственный интеллект" - техническая программа
• "Управление ИИ-продуктами/AI Product" - продуктовая программа

💡 **Что я умею:**
✅ Отвечать на вопросы о программах
✅ Сравнивать программы по критериям
✅ Давать персональные рекомендации
✅ Помогать с планированием поступления
✅ Рекомендовать выборные дисциплины

Выбери действие из меню ниже:
"""

    if not existing_profile:
        welcome_text += "\n🆕 *Рекомендую сначала настроить профиль для персональных рекомендаций*"

    await message.answer(welcome_text, reply_markup=create_main_menu(), parse_mode="Markdown")


@router.callback_query(F.data == "main_menu")
async def show_main_menu(callback: CallbackQuery):
    """Show main menu"""
    await callback.message.edit_text(
        "🏠 **Главное меню**\n\nВыберите действие:",
        reply_markup=create_main_menu(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "ask_question")
async def ask_question_mode(callback: CallbackQuery, state: FSMContext):
    """Enable question mode"""
    await callback.message.edit_text(
        "🤖 **Режим вопросов активирован**\n\n"
        "Задайте любой вопрос о магистерских программах ИТМО по ИИ.\n"
        "Например:\n"
        "• Чем отличаются программы?\n"
        "• Какие требования для поступления?\n"
        "• Какие карьерные перспективы?\n"
        "• Сколько стоит обучение?\n\n"
        "💬 Напишите ваш вопрос следующим сообщением:",
        parse_mode="Markdown",
    )
    await state.set_state("waiting_for_question")
    await callback.answer()


@router.message(StateFilter("waiting_for_question"))
async def process_question(message: Message, state: FSMContext):
    """Process user question"""
    user_question = message.text
    user_id = message.from_user.id

    # Show typing indicator
    await message.bot.send_chat_action(message.chat.id, "typing")

    try:
        # Get AI response
        ai_response = await ai_assistant.get_response(user_question, user_id)

        # Send response with main menu
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="❓ Задать еще вопрос", callback_data="ask_question")],
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
            ]
        )

        await message.answer(ai_response, reply_markup=keyboard, parse_mode="Markdown")

    except Exception:
        await message.answer(
            "Извините, произошла ошибка при обработке вашего вопроса. Попробуйте еще раз.",
            reply_markup=create_main_menu(),
        )

    await state.clear()


@router.callback_query(F.data == "compare_programs")
async def compare_programs(callback: CallbackQuery):
    """Show programs comparison"""
    await callback.message.edit_text("🔄 Генерирую сравнение программ...")
    await callback.answer()

    try:
        comparison = ai_assistant.compare_programs()

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🎯 Получить рекомендацию", callback_data="get_recommendation"
                    )
                ],
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
            ]
        )

        await callback.message.edit_text(comparison, reply_markup=keyboard, parse_mode="Markdown")

    except Exception:
        await callback.message.edit_text(
            "Ошибка при генерации сравнения. Попробуйте позже.", reply_markup=create_main_menu()
        )


@router.callback_query(F.data == "get_recommendation")
async def get_recommendation(callback: CallbackQuery):
    """Get personalized recommendation"""
    user_id = callback.from_user.id
    user_profile = db.get_user_profile(user_id)

    if not user_profile:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✏️ Настроить профиль", callback_data="setup_profile")],
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
            ]
        )

        await callback.message.edit_text(
            "🎯 **Персональные рекомендации**\n\n"
            "Для получения персональных рекомендаций необходимо заполнить профиль.\n\n"
            "Профиль поможет мне:\n"
            "• Понять ваш технический бэкграунд\n"
            "• Узнать ваши карьерные цели\n"
            "• Предложить подходящую программу\n"
            "• Рекомендовать выборные дисциплины",
            reply_markup=keyboard,
            parse_mode="Markdown",
        )
        await callback.answer()
        return

    await callback.message.edit_text("🔄 Генерирую персональную рекомендацию...")
    await callback.answer()

    try:
        recommendation = ai_assistant.generate_program_recommendation(user_profile)

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Обновить профиль", callback_data="update_profile")],
                [
                    InlineKeyboardButton(
                        text="📚 Гид по поступлению", callback_data="admission_guide"
                    )
                ],
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
            ]
        )

        await callback.message.edit_text(
            f"🎯 **Персональная рекомендация**\n\n{recommendation}",
            reply_markup=keyboard,
            parse_mode="Markdown",
        )

    except Exception:
        await callback.message.edit_text(
            "Ошибка при генерации рекомендации. Попробуйте позже.", reply_markup=create_main_menu()
        )


@router.callback_query(F.data == "admission_guide")
async def admission_guide(callback: CallbackQuery):
    """Show admission guide"""
    await callback.message.edit_text("📚 Генерирую гид по поступлению...")
    await callback.answer()

    try:
        guide = ai_assistant.generate_admission_guide()

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🎯 Получить рекомендацию", callback_data="get_recommendation"
                    )
                ],
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
            ]
        )

        await callback.message.edit_text(guide, reply_markup=keyboard, parse_mode="Markdown")

    except Exception:
        await callback.message.edit_text(
            "Ошибка при генерации гида. Попробуйте позже.", reply_markup=create_main_menu()
        )


@router.callback_query(F.data == "user_profile")
async def user_profile_menu(callback: CallbackQuery):
    """Show user profile menu"""
    await callback.message.edit_text(
        "👤 **Управление профилем**\n\n"
        "Профиль помогает получать персональные рекомендации по программам и планированию обучения.",
        reply_markup=create_profile_menu(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "view_profile")
async def view_profile(callback: CallbackQuery):
    """View user profile"""
    user_id = callback.from_user.id
    user_profile = db.get_user_profile(user_id)

    if not user_profile:
        await callback.message.edit_text(
            "👤 **Мой профиль**\n\n"
            "❌ Профиль не заполнен.\n\n"
            "Заполните профиль для получения персональных рекомендаций.",
            reply_markup=create_profile_menu(),
            parse_mode="Markdown",
        )
        await callback.answer()
        return

    profile_text = f"""
👤 **Мой профиль**

🏷️ **Имя:** {user_profile.username}
📚 **Интересы:** {', '.join(user_profile.interests) if user_profile.interests else 'не указаны'}
💻 **Технические навыки:** {', '.join(user_profile.technical_skills) if user_profile.technical_skills else 'не указаны'}
🎯 **Карьерные цели:** {', '.join(user_profile.career_goals) if user_profile.career_goals else 'не указаны'}
📖 **Предпочитаемая программа:** {user_profile.preferred_program or 'не выбрана'}

📅 **Создан:** {user_profile.created_at[:10] if user_profile.created_at else 'N/A'}
🔄 **Обновлен:** {user_profile.updated_at[:10] if user_profile.updated_at else 'N/A'}
"""

    await callback.message.edit_text(
        profile_text, reply_markup=create_profile_menu(), parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data.in_(["setup_profile", "update_profile"]))
async def setup_profile(callback: CallbackQuery, state: FSMContext):
    """Start profile setup"""
    await callback.message.edit_text(
        "✏️ **Настройка профиля**\n\n"
        "Расскажите немного о своем образовательном/профессиональном бэкграунде.\n\n"
        "Например:\n"
        "• Какое у вас образование\n"
        "• Опыт работы\n"
        "• Проекты, над которыми работали\n"
        "• Что изучали самостоятельно\n\n"
        "💬 Напишите ваш ответ:"
    )
    await state.set_state(ProfileStates.waiting_for_background)
    await callback.answer()


@router.message(ProfileStates.waiting_for_background)
async def process_background(message: Message, state: FSMContext):
    """Process background information"""
    await state.update_data(background=message.text)

    await message.answer(
        "🎯 **Ваши интересы**\n\n"
        "Какие области ИИ/ML вас больше всего интересуют?\n\n"
        "Например:\n"
        "• Машинное обучение\n"
        "• Компьютерное зрение\n"
        "• NLP\n"
        "• Продуктовая аналитика\n"
        "• AI продукты\n\n"
        "💬 Перечислите через запятую:"
    )
    await state.set_state(ProfileStates.waiting_for_interests)


@router.message(ProfileStates.waiting_for_interests)
async def process_interests(message: Message, state: FSMContext):
    """Process interests"""
    interests = [interest.strip() for interest in message.text.split(",")]
    await state.update_data(interests=interests)

    await message.answer(
        "💻 **Технические навыки**\n\n"
        "Какими языками программирования, фреймворками или инструментами вы владеете?\n\n"
        "Например:\n"
        "• Python, R, SQL\n"
        "• TensorFlow, PyTorch\n"
        "• Docker, Git\n"
        "• Jupyter, Pandas\n\n"
        "💬 Перечислите через запятую:"
    )
    await state.set_state(ProfileStates.waiting_for_skills)


@router.message(ProfileStates.waiting_for_skills)
async def process_skills(message: Message, state: FSMContext):
    """Process technical skills"""
    skills = [skill.strip() for skill in message.text.split(",")]
    await state.update_data(skills=skills)

    await message.answer(
        "🎯 **Карьерные цели**\n\n"
        "Какие у вас карьерные планы после окончания магистратуры?\n\n"
        "Например:\n"
        "• ML Engineer в крупной компании\n"
        "• Product Manager в AI стартапе\n"
        "• Data Scientist\n"
        "• Исследователь в университете\n"
        "• Основать собственную компанию\n\n"
        "💬 Опишите ваши цели:"
    )
    await state.set_state(ProfileStates.waiting_for_goals)


@router.message(ProfileStates.waiting_for_goals)
async def process_goals(message: Message, state: FSMContext):
    """Process career goals and save profile"""
    goals = [goal.strip() for goal in message.text.split(",") if goal.strip()]
    user_data = await state.get_data()

    # Create user profile
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or "Пользователь"
    now = datetime.now().isoformat()

    profile = UserProfile(
        user_id=user_id,
        username=username,
        background={"description": user_data.get("background", "")},
        interests=user_data.get("interests", []),
        technical_skills=user_data.get("skills", []),
        career_goals=goals,
        preferred_program=None,
        created_at=now,
        updated_at=now,
    )

    success = db.save_user_profile(profile)

    if success:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🎯 Получить рекомендацию", callback_data="get_recommendation"
                    )
                ],
                [InlineKeyboardButton(text="👀 Посмотреть профиль", callback_data="view_profile")],
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
            ]
        )

        await message.answer(
            "✅ **Профиль успешно сохранен!**\n\n"
            "Теперь вы можете получить персональные рекомендации по программам и планированию обучения.",
            reply_markup=keyboard,
            parse_mode="Markdown",
        )
    else:
        await message.answer(
            "❌ Ошибка при сохранении профиля. Попробуйте еще раз.", reply_markup=create_main_menu()
        )

    await state.clear()


@router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery):
    """Show help information"""
    help_text = """
ℹ️ **Справка**

🤖 **О боте:**
Я помогаю абитуриентам выбрать между двумя магистерскими программами ИТМО в области ИИ и спланировать обучение.

📚 **Доступные программы:**
• "Искусственный интеллект" - техническая программа
• "Управление ИИ-продуктами/AI Product" - продуктовая программа

🔧 **Возможности:**
• Ответы на вопросы о программах
• Сравнение программ по критериям
• Персональные рекомендации на основе профиля
• Гид по поступлению
• Рекомендации по выборным дисциплинам

⚠️ **Важно:**
Я отвечаю только на вопросы, связанные с этими двумя программами магистратуры ИТМО.

📞 **Команды:**
/start - перезапустить бота
/help - показать справку

👤 **Профиль:**
Заполните профиль для получения персональных рекомендаций!
"""

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👤 Настроить профиль", callback_data="setup_profile")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
        ]
    )

    await callback.message.edit_text(help_text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command"""
    await show_help(
        CallbackQuery(
            id="help_cmd",
            from_user=message.from_user,
            chat_instance="help",
            data="help",
            message=message,
        )
    )


# Fallback handler for any other messages
@router.message()
async def handle_other_messages(message: Message):
    """Handle any other messages as questions"""
    user_id = message.from_user.id
    user_question = message.text

    # Show typing indicator
    await message.bot.send_chat_action(message.chat.id, "typing")

    try:
        # Get AI response
        ai_response = await ai_assistant.get_response(user_question, user_id)

        # Send response with main menu
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="❓ Задать еще вопрос", callback_data="ask_question")],
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
            ]
        )

        await message.answer(ai_response, reply_markup=keyboard, parse_mode="Markdown")

    except Exception:
        await message.answer(
            "Произошла ошибка при обработке сообщения. Попробуйте использовать меню.",
            reply_markup=create_main_menu(),
        )
