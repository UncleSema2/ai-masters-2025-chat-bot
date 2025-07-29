"""
Integration tests for Telegram bot handlers
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from handlers.user_handlers import (
    ask_question_mode,
    cmd_start,
    compare_programs,
    get_recommendation,
    process_background,
    process_goals,
    process_interests,
    process_question,
    process_skills,
    setup_profile,
    show_main_menu,
)


@pytest.mark.integration
@pytest.mark.asyncio
class TestBotHandlers:
    """Test Telegram bot handlers integration"""

    async def test_cmd_start_new_user(self, mock_message, temp_db):
        """Test /start command for new user"""
        with patch("handlers.user_handlers.db", temp_db):
            await cmd_start(mock_message)

        # Verify welcome message was sent
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args
        message_text = call_args[0][0]

        assert "Добро пожаловать" in message_text
        assert "Рекомендую сначала настроить профиль" in message_text

        # Verify reply markup was provided
        assert call_args[1]["reply_markup"] is not None

    async def test_cmd_start_existing_user(self, mock_message, temp_db, sample_user_profile):
        """Test /start command for existing user"""
        # Add user profile to database
        temp_db.save_user_profile(sample_user_profile)

        # Mock message from existing user
        mock_message.from_user.id = sample_user_profile.user_id

        with patch("handlers.user_handlers.db", temp_db):
            await cmd_start(mock_message)

        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args
        message_text = call_args[0][0]

        assert "Добро пожаловать" in message_text
        # Should not suggest profile setup for existing users
        assert "Рекомендую сначала настроить профиль" not in message_text

    async def test_show_main_menu(self, mock_callback_query):
        """Test showing main menu"""
        await show_main_menu(mock_callback_query)

        mock_callback_query.message.edit_text.assert_called_once()
        call_args = mock_callback_query.message.edit_text.call_args

        assert "Главное меню" in call_args[0][0]
        assert call_args[1]["reply_markup"] is not None
        mock_callback_query.answer.assert_called_once()

    async def test_ask_question_mode(self, mock_callback_query):
        """Test activating question mode"""
        mock_state = AsyncMock()

        await ask_question_mode(mock_callback_query, mock_state)

        mock_callback_query.message.edit_text.assert_called_once()
        call_args = mock_callback_query.message.edit_text.call_args

        assert "Режим вопросов активирован" in call_args[0][0]
        mock_state.set_state.assert_called_once_with("waiting_for_question")
        mock_callback_query.answer.assert_called_once()

    async def test_process_question_relevant(self, mock_message, temp_db, sample_program):
        """Test processing relevant question"""
        # Add sample program to database
        temp_db.save_program(sample_program)

        mock_message.text = "Чем отличаются программы?"
        mock_state = AsyncMock()

        with (
            patch("handlers.user_handlers.db", temp_db),
            patch("handlers.user_handlers.ai_assistant") as mock_ai,
        ):

            # Mock async method properly
            mock_ai.get_response = AsyncMock(return_value="Программы отличаются фокусом...")

            await process_question(mock_message, mock_state)

        # Verify AI assistant was called
        mock_ai.get_response.assert_called_once_with(mock_message.text, mock_message.from_user.id)

        # Verify response was sent
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args
        assert "Программы отличаются фокусом..." in call_args[0][0]

        # Verify state was cleared
        mock_state.clear.assert_called_once()

    async def test_process_question_with_error(self, mock_message):
        """Test processing question with AI error"""
        mock_message.text = "Test question"
        mock_state = AsyncMock()

        with patch("handlers.user_handlers.ai_assistant") as mock_ai:
            mock_ai.get_response.side_effect = Exception("AI Error")

            await process_question(mock_message, mock_state)

        # Verify error message was sent
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args
        assert "произошла ошибка" in call_args[0][0]

    async def test_compare_programs_success(self, mock_callback_query, temp_db, sample_program):
        """Test successful programs comparison"""
        # Add sample program to database
        temp_db.save_program(sample_program)

        with patch("handlers.user_handlers.ai_assistant") as mock_ai:
            mock_ai.compare_programs.return_value = "Сравнение программ: ..."

            await compare_programs(mock_callback_query)

        # Verify loading message was shown
        assert mock_callback_query.message.edit_text.call_count >= 1

        # Verify AI assistant was called
        mock_ai.compare_programs.assert_called_once()

        # Verify final response
        final_call = mock_callback_query.message.edit_text.call_args_list[-1]
        assert "Сравнение программ: ..." in final_call[0][0]

    async def test_compare_programs_error(self, mock_callback_query):
        """Test programs comparison with error"""
        with patch("handlers.user_handlers.ai_assistant") as mock_ai:
            mock_ai.compare_programs.side_effect = Exception("AI Error")

            await compare_programs(mock_callback_query)

        # Verify error message was shown
        final_call = mock_callback_query.message.edit_text.call_args_list[-1]
        assert "Ошибка при генерации сравнения" in final_call[0][0]

    async def test_get_recommendation_no_profile(self, mock_callback_query, temp_db):
        """Test getting recommendation without user profile"""
        with patch("handlers.user_handlers.db", temp_db):
            await get_recommendation(mock_callback_query)

        # Verify message asking to setup profile
        mock_callback_query.message.edit_text.assert_called_once()
        call_args = mock_callback_query.message.edit_text.call_args

        assert "необходимо заполнить профиль" in call_args[0][0]
        # Verify setup profile button is provided
        assert call_args[1]["reply_markup"] is not None

    async def test_get_recommendation_with_profile(
        self, mock_callback_query, temp_db, sample_user_profile, sample_program
    ):
        """Test getting recommendation with user profile"""
        # Add data to database
        temp_db.save_user_profile(sample_user_profile)
        temp_db.save_program(sample_program)

        mock_callback_query.from_user.id = sample_user_profile.user_id

        with (
            patch("handlers.user_handlers.db", temp_db),
            patch("handlers.user_handlers.ai_assistant") as mock_ai,
        ):

            mock_ai.generate_program_recommendation.return_value = "Рекомендация: ..."

            await get_recommendation(mock_callback_query)

        # Verify AI assistant was called with user profile
        mock_ai.generate_program_recommendation.assert_called_once()

        # Verify recommendation was shown
        final_call = mock_callback_query.message.edit_text.call_args_list[-1]
        assert "Рекомендация: ..." in final_call[0][0]

    async def test_setup_profile_flow(self, mock_callback_query):
        """Test starting profile setup"""
        mock_state = AsyncMock()

        await setup_profile(mock_callback_query, mock_state)

        # Verify profile setup message
        mock_callback_query.message.edit_text.assert_called_once()
        call_args = mock_callback_query.message.edit_text.call_args

        assert "Настройка профиля" in call_args[0][0]
        assert "бэкграунде" in call_args[0][0]

        # Verify state was set
        mock_state.set_state.assert_called_once()

    async def test_profile_setup_complete_flow(self, mock_message, temp_db):
        """Test complete profile setup flow"""
        mock_state = AsyncMock()

        # Test background processing
        mock_message.text = "Бакалавр информатики, работал Python разработчиком"
        mock_state.update_data = AsyncMock()

        await process_background(mock_message, mock_state)

        mock_state.update_data.assert_called_once_with(background=mock_message.text)
        mock_message.answer.assert_called_once()

        # Verify next step message
        call_args = mock_message.answer.call_args
        assert "интересы" in call_args[0][0]

        # Test interests processing
        mock_message.text = "машинное обучение, NLP, компьютерное зрение"

        await process_interests(mock_message, mock_state)

        # Test skills processing
        mock_message.text = "Python, TensorFlow, SQL, Git"

        await process_skills(mock_message, mock_state)

        # Test final goals processing and profile saving
        mock_message.text = "ML Engineer, Data Scientist"
        mock_state.get_data = AsyncMock(
            return_value={
                "background": "Бакалавр информатики",
                "interests": ["машинное обучение", "NLP"],
                "skills": ["Python", "TensorFlow"],
            }
        )

        with patch("handlers.user_handlers.db", temp_db):
            await process_goals(mock_message, mock_state)

        # Verify profile was saved
        saved_profile = temp_db.get_user_profile(mock_message.from_user.id)
        assert saved_profile is not None
        assert saved_profile.user_id == mock_message.from_user.id

        # Verify success message
        final_call = mock_message.answer.call_args
        assert "успешно сохранен" in final_call[0][0]

        # Verify state was cleared
        mock_state.clear.assert_called_once()

    async def test_profile_setup_save_error(self, mock_message):
        """Test profile setup with save error"""
        mock_state = AsyncMock()
        mock_message.text = "ML Engineer"
        mock_state.get_data = AsyncMock(
            return_value={
                "background": "Test background",
                "interests": ["test"],
                "skills": ["Python"],
            }
        )

        # Mock database save failure
        mock_db = MagicMock()
        mock_db.save_user_profile.return_value = False

        with patch("handlers.user_handlers.db", mock_db):
            await process_goals(mock_message, mock_state)

        # Verify error message
        call_args = mock_message.answer.call_args
        assert "Ошибка при сохранении" in call_args[0][0]


@pytest.mark.integration
class TestHandlerHelpers:
    """Test handler helper functions"""

    def test_create_main_menu(self):
        """Test main menu keyboard creation"""
        from handlers.user_handlers import create_main_menu

        keyboard = create_main_menu()

        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == 6  # 6 menu items

        # Check button texts
        button_texts = []
        for row in keyboard.inline_keyboard:
            for button in row:
                button_texts.append(button.text)

        assert "🤖 Задать вопрос" in button_texts
        assert "📊 Сравнить программы" in button_texts
        assert "🎯 Получить рекомендацию" in button_texts

    def test_create_profile_menu(self):
        """Test profile menu keyboard creation"""
        from handlers.user_handlers import create_profile_menu

        keyboard = create_profile_menu()

        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == 4  # 4 profile menu items

        # Check button texts
        button_texts = []
        for row in keyboard.inline_keyboard:
            for button in row:
                button_texts.append(button.text)

        assert "✏️ Настроить профиль" in button_texts
        assert "👀 Посмотреть профиль" in button_texts
        assert "🔄 Обновить профиль" in button_texts
        assert "🏠 Главное меню" in button_texts
