"""
Unit tests for AI assistant module
"""

from unittest.mock import patch

import pytest

from models.database import UserProfile
from utils.ai_assistant import AIAssistant


@pytest.mark.unit
class TestAIAssistant:
    """Test AIAssistant class"""

    def test_ai_assistant_initialization(self, mock_openai_client):
        """Test AI assistant initialization"""
        with patch("utils.ai_assistant.openai.OpenAI", return_value=mock_openai_client):
            assistant = AIAssistant()
            assert assistant.client == mock_openai_client
            assert assistant.model == "gpt-4.1-mini-2025-04-14"
            assert assistant.db is not None

    def test_get_programs_context(self, ai_assistant_with_mock_db: AIAssistant, sample_program):
        """Test getting programs context for AI"""
        # Add sample program to database
        ai_assistant_with_mock_db.db.save_program(sample_program)

        context = ai_assistant_with_mock_db.get_programs_context()

        assert "ПРОГРАММА: Искусственный интеллект" in context
        assert "институт прикладных компьютерных наук" in context
        assert "2 года" in context
        assert "ML Engineer" in context
        assert "X5 Group" in context

    def test_get_programs_context_empty_db(self, ai_assistant_with_mock_db: AIAssistant):
        """Test getting programs context from empty database"""
        context = ai_assistant_with_mock_db.get_programs_context()
        assert context == ""

    def test_format_directions(self, ai_assistant_with_mock_db: AIAssistant):
        """Test formatting directions for context"""
        directions = [
            {
                "name": "Информатика и вычислительная техника",
                "code": "09.04.01",
                "budget_places": 51,
                "target_places": 4,
                "contract_places": 55,
            }
        ]

        formatted = ai_assistant_with_mock_db._format_directions(directions)

        assert "Информатика и вычислительная техника" in formatted
        assert "09.04.01" in formatted
        assert "Бюджет: 51" in formatted
        assert "Целевые: 4" in formatted
        assert "Контракт: 55" in formatted

    def test_format_directions_empty(self, ai_assistant_with_mock_db: AIAssistant):
        """Test formatting empty directions"""
        formatted = ai_assistant_with_mock_db._format_directions([])
        assert formatted == "Информация о направлениях не найдена"

    def test_format_faq(self, ai_assistant_with_mock_db: AIAssistant):
        """Test formatting FAQ for context"""
        faq = [
            {
                "question": "Можно ли поступить без профильного образования?",
                "answer": "Да, но нужно будет пройти вступительные испытания.",
            },
            {"question": "Сколько стоит обучение?", "answer": "599 000 рублей в год."},
        ]

        formatted = ai_assistant_with_mock_db._format_faq(faq)

        assert "Q: Можно ли поступить без профильного образования?" in formatted
        assert "A: Да, но нужно будет пройти вступительные испытания." in formatted
        assert "Q: Сколько стоит обучение?" in formatted

    def test_format_faq_empty(self, ai_assistant_with_mock_db: AIAssistant):
        """Test formatting empty FAQ"""
        formatted = ai_assistant_with_mock_db._format_faq([])
        assert formatted == "FAQ не найден"

    def test_is_relevant_question_relevant(self, ai_assistant_with_mock_db: AIAssistant):
        """Test relevant question detection"""
        relevant_questions = [
            "Чем отличаются программы ИТМО по ИИ?",
            "Какие требования для поступления на магистратуру?",
            "Сколько стоит обучение по искусственному интеллекту?",
            "Какие карьерные перспективы после программы ML?",
            "Как подать документы в магистратуру ИТМО?",
        ]

        for question in relevant_questions:
            assert ai_assistant_with_mock_db.is_relevant_question(question) is True

    def test_is_relevant_question_irrelevant(self, ai_assistant_with_mock_db: AIAssistant):
        """Test irrelevant question detection"""
        irrelevant_questions = [
            "Какая сегодня погода?",
            "Кто выиграл в футболе?",
            "Как приготовить борщ?",
            "Какой фильм посмотреть?",
            "Где купить автомобиль?",
        ]

        for question in irrelevant_questions:
            assert ai_assistant_with_mock_db.is_relevant_question(question) is False

    def test_is_relevant_question_borderline(self, ai_assistant_with_mock_db: AIAssistant):
        """Test borderline question detection"""
        # Short questions should be considered irrelevant
        assert ai_assistant_with_mock_db.is_relevant_question("Да") is False
        assert ai_assistant_with_mock_db.is_relevant_question("Нет нет") is False

        # Longer questions without clear irrelevant keywords should be considered relevant
        long_neutral = "Расскажите подробнее о возможностях данного направления"
        assert ai_assistant_with_mock_db.is_relevant_question(long_neutral) is True

        # Questions with relevant keywords should be relevant
        assert ai_assistant_with_mock_db.is_relevant_question("Чем отличаются программы?") is True

    @pytest.mark.asyncio
    async def test_get_response_relevant_question(
        self, ai_assistant_with_mock_db: AIAssistant, sample_program
    ):
        """Test getting response for relevant question"""
        # Add sample program to database
        ai_assistant_with_mock_db.db.save_program(sample_program)

        user_id = 12345
        question = "Чем отличаются программы?"

        response = await ai_assistant_with_mock_db.get_response(question, user_id)

        assert response == "Мокированный ответ от AI ассистента для тестирования."
        # Verify OpenAI client was called
        ai_assistant_with_mock_db.client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_response_irrelevant_question(self, ai_assistant_with_mock_db: AIAssistant):
        """Test getting response for irrelevant question"""
        user_id = 12345
        question = "Какая сегодня погода?"

        response = await ai_assistant_with_mock_db.get_response(question, user_id)

        assert "Я специализируюсь только на вопросах" in response
        assert "магистерскими программами ИТМО" in response
        # Verify OpenAI client was NOT called
        ai_assistant_with_mock_db.client.chat.completions.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_response_with_user_profile(
        self,
        ai_assistant_with_mock_db: AIAssistant,
        sample_user_profile: UserProfile,
        sample_program,
    ):
        """Test getting response with user profile context"""
        # Add data to database
        ai_assistant_with_mock_db.db.save_program(sample_program)
        ai_assistant_with_mock_db.db.save_user_profile(sample_user_profile)

        user_id = sample_user_profile.user_id
        question = "Какая программа мне подойдет?"

        response = await ai_assistant_with_mock_db.get_response(question, user_id)

        assert response == "Мокированный ответ от AI ассистента для тестирования."

        # Check that user profile was included in the prompt
        call_args = ai_assistant_with_mock_db.client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        user_message = messages[1]["content"]

        assert "ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ:" in user_message
        assert "машинное обучение" in user_message
        assert "Python" in user_message

    @pytest.mark.asyncio
    async def test_get_response_api_error(self, ai_assistant_with_mock_db: AIAssistant):
        """Test handling API errors"""
        # Mock API error
        ai_assistant_with_mock_db.client.chat.completions.create.side_effect = Exception(
            "API Error"
        )

        user_id = 12345
        question = "Какие программы доступны?"

        response = await ai_assistant_with_mock_db.get_response(question, user_id)

        assert "произошла ошибка при обработке" in response

    def test_generate_program_recommendation(
        self,
        ai_assistant_with_mock_db: AIAssistant,
        sample_user_profile: UserProfile,
        sample_program,
    ):
        """Test generating program recommendation"""
        # Add sample program to database
        ai_assistant_with_mock_db.db.save_program(sample_program)

        recommendation = ai_assistant_with_mock_db.generate_program_recommendation(
            sample_user_profile
        )

        assert recommendation == "Мокированный ответ от AI ассистента для тестирования."

        # Check that user profile was included in the prompt
        call_args = ai_assistant_with_mock_db.client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        user_message = messages[1]["content"]

        assert "ПРОФИЛЬ АБИТУРИЕНТА:" in user_message
        assert "машинное обучение" in user_message
        assert "ML Engineer в крупной компании" in user_message

    def test_generate_program_recommendation_error(
        self, ai_assistant_with_mock_db: AIAssistant, sample_user_profile: UserProfile
    ):
        """Test handling errors in recommendation generation"""
        # Mock API error
        ai_assistant_with_mock_db.client.chat.completions.create.side_effect = Exception(
            "API Error"
        )

        recommendation = ai_assistant_with_mock_db.generate_program_recommendation(
            sample_user_profile
        )

        assert "Не удалось сгенерировать рекомендацию" in recommendation

    def test_compare_programs(self, ai_assistant_with_mock_db: AIAssistant, sample_program):
        """Test programs comparison"""
        # Add sample program to database
        ai_assistant_with_mock_db.db.save_program(sample_program)

        comparison = ai_assistant_with_mock_db.compare_programs()

        assert comparison == "Мокированный ответ от AI ассистента для тестирования."

        # Check that prompt includes comparison task
        call_args = ai_assistant_with_mock_db.client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        user_message = messages[1]["content"]

        assert "Сравни программы по следующим критериям" in user_message

    def test_compare_programs_error(self, ai_assistant_with_mock_db: AIAssistant):
        """Test handling errors in programs comparison"""
        # Mock API error
        ai_assistant_with_mock_db.client.chat.completions.create.side_effect = Exception(
            "API Error"
        )

        comparison = ai_assistant_with_mock_db.compare_programs()

        assert "Не удалось выполнить сравнение программ" in comparison

    def test_generate_admission_guide(self, ai_assistant_with_mock_db: AIAssistant, sample_program):
        """Test generating admission guide"""
        # Add sample program to database
        ai_assistant_with_mock_db.db.save_program(sample_program)

        guide = ai_assistant_with_mock_db.generate_admission_guide()

        assert guide == "Мокированный ответ от AI ассистента для тестирования."

        # Check that prompt includes admission guide task
        call_args = ai_assistant_with_mock_db.client.chat.completions.create.call_args
        messages = call_args[1]["messages"]
        user_message = messages[1]["content"]

        assert "подробный гид по поступлению" in user_message

    def test_generate_admission_guide_error(self, ai_assistant_with_mock_db: AIAssistant):
        """Test handling errors in admission guide generation"""
        # Mock API error
        ai_assistant_with_mock_db.client.chat.completions.create.side_effect = Exception(
            "API Error"
        )

        guide = ai_assistant_with_mock_db.generate_admission_guide()

        assert "Не удалось создать гид по поступлению" in guide
