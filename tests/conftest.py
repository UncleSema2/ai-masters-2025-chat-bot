"""
Pytest configuration and fixtures for AI Master 2025 Chatbot tests
"""

import os
import tempfile
from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from config import Settings
from models.database import Database, Program, UserProfile
from utils.ai_assistant import AIAssistant


@pytest.fixture
def temp_db() -> Generator[Database, None, None]:
    """Create temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name

    try:
        db = Database(db_path)
        yield db
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)


@pytest.fixture
def sample_program_data() -> dict[str, Any]:
    """Sample program data for testing"""
    return {
        "name": "Искусственный интеллект",
        "url": "https://abit.itmo.ru/program/master/ai",
        "institute": "институт прикладных компьютерных наук",
        "duration": "2 года",
        "language": "русский",
        "cost": "599 000 ₽",
        "description": "Создавайте AI-продукты и технологии, которые меняют мир.",
        "directions": [
            {
                "name": "Информатика и вычислительная техника",
                "code": "09.04.01",
                "budget_places": 51,
                "target_places": 4,
                "contract_places": 55,
            }
        ],
        "career_prospects": ["ML Engineer", "Data Engineer", "AI Product Developer"],
        "partners": ["X5 Group", "Ozon Bank", "МТС"],
        "team": [
            {
                "name": "Дмитрий Сергеевич Ботов",
                "position": "Руководитель программы",
                "description": "кандидат технических наук",
            }
        ],
        "admission_ways": ["Вступительный экзамен", "Конкурс Junior ML Contest"],
        "faq": [
            {
                "question": "Можно ли поступить без профильного образования?",
                "answer": "Да, но нужно будет пройти вступительные испытания.",
            }
        ],
        "exam_dates": ["29.07.2025, 11:00", "31.07.2025, 11:00"],
        "created_at": "2025-01-01T12:00:00",
        "updated_at": "2025-01-01T12:00:00",
    }


@pytest.fixture
def sample_program(sample_program_data: dict[str, Any]) -> Program:
    """Create sample Program object"""
    return Program(**sample_program_data)


@pytest.fixture
def sample_user_profile() -> UserProfile:
    """Sample user profile for testing"""
    return UserProfile(
        user_id=12345,
        username="test_user",
        background={"description": "Бакалавр по информатике, работал Junior Python Developer"},
        interests=["машинное обучение", "компьютерное зрение", "NLP"],
        technical_skills=["Python", "TensorFlow", "SQL", "Git"],
        career_goals=["ML Engineer в крупной компании", "Data Scientist"],
        preferred_program=None,
        created_at="2025-01-01T12:00:00",
        updated_at="2025-01-01T12:00:00",
    )


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing"""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()

    mock_message.content = "Мокированный ответ от AI ассистента для тестирования."
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response

    return mock_client


@pytest.fixture
def mock_settings() -> Settings:
    """Mock settings for testing"""
    settings = MagicMock(spec=Settings)
    settings.telegram_bot_token = "test_bot_token"
    settings.openai_api_key = "test_openai_key"
    settings.openai_model = "gpt-4.1-mini-2025-04-14"
    settings.database_url = "sqlite:///:memory:"
    settings.debug = True
    settings.log_level = "DEBUG"
    settings.request_delay = 0
    settings.user_agent = "Test-Agent/1.0"
    return settings


@pytest.fixture
def ai_assistant_with_mock_db(temp_db: Database, mock_openai_client) -> AIAssistant:
    """AI Assistant with mocked OpenAI client and temp database"""
    with patch("utils.ai_assistant.openai.OpenAI", return_value=mock_openai_client):
        assistant = AIAssistant()
        assistant.db = temp_db
        assistant.client = mock_openai_client
        return assistant


@pytest.fixture
def sample_html_ai_program() -> str:
    """Sample HTML content for AI program page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Искусственный интеллект</title>
    </head>
    <body>
        <h1>Искусственный интеллект</h1>
        <div class="program-info">
            <p>форма обучения: очная</p>
            <p>длительность: 2 года</p>
            <p>язык обучения: русский</p>
            <p>стоимость контрактного обучения (год): 599 000 ₽</p>
        </div>
        <section id="about">
            <h2>о программе</h2>
            <div>
                <p>Создавайте AI-продукты и технологии, которые меняют мир.</p>
                <p>Основа обучения на программе – проектный подход.</p>
            </div>
        </section>
        <section class="directions">
            <h5>Информатика и вычислительная техника</h5>
            <p>09.04.01</p>
            <p>51 бюджетных</p>
            <p>4 целевая</p>
            <p>55 контрактных</p>
        </section>
        <section class="career">
            <h2>Карьера</h2>
            <div>
                <p>– ML Engineer – создает и внедряет ML-модели в продакшен;</p>
                <p>– Data Engineer – выстраивает процессы сбора, хранения и обработки данных;</p>
            </div>
        </section>
        <div class="partners">
            <img src="/images/x5group.png" alt="X5 Group">
            <img src="/images/ozonbank.png" alt="Ozon Bank">
        </div>
        <div class="exam-dates">
            <div>29.07.2025, 11:00</div>
            <div>31.07.2025, 11:00</div>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def sample_html_ai_product() -> str:
    """Sample HTML content for AI Product program page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Управление ИИ-продуктами/AI Product</title>
    </head>
    <body>
        <h1>Управление ИИ-продуктами/AI Product</h1>
        <div class="program-info">
            <p>форма обучения: очная</p>
            <p>длительность: 2 года</p>
            <p>язык обучения: русский</p>
            <p>стоимость контрактного обучения (год): 599 000 ₽</p>
        </div>
        <section id="about">
            <h2>о программе</h2>
            <div>
                <p>Программа дает глубокие технические знания в области разработки систем ИИ и навыки продуктового менеджмента.</p>
            </div>
        </section>
        <section class="directions">
            <h5>Математическое обеспечение и администрирование информационных систем</h5>
            <p>02.04.03</p>
            <p>14 бюджетных</p>
            <p>0 целевая</p>
            <p>50 контрактных</p>
        </section>
        <section class="career">
            <h2>Карьера</h2>
            <div>
                <p>– AI Product Manager</p>
                <p>– AI Project Manager</p>
                <p>– Product Data Analyst</p>
            </div>
        </section>
        <div class="partners">
            <img src="/images/alphabank.png" alt="Альфа-Банк">
        </div>
    </body>
    </html>
    """


@pytest.fixture
def mock_requests_response():
    """Mock requests response for testing web scraping"""

    def _mock_response(content: str, status_code: int = 200):
        mock_response = MagicMock()
        mock_response.content = content.encode("utf-8")
        mock_response.status_code = status_code
        mock_response.raise_for_status.return_value = None
        return mock_response

    return _mock_response


@pytest.fixture
def sample_test_data() -> dict[str, Any]:
    """Sample test data for various tests"""
    return {
        "telegram_user_id": 12345,
        "telegram_username": "test_user",
        "test_questions": [
            "Чем отличаются программы?",
            "Какие требования для поступления?",
            "Сколько стоит обучение?",
            "Какие карьерные перспективы?",
        ],
        "irrelevant_questions": [
            "Какая сегодня погода?",
            "Как приготовить борщ?",
            "Кто выиграл в футболе?",
        ],
        "ai_responses": [
            'Программа "Искусственный интеллект" фокусируется на технических аспектах...',
            "Для поступления необходимо пройти вступительные испытания...",
            "Стоимость обучения составляет 599 000 рублей в год...",
        ],
    }


# Async fixtures for aiogram testing
@pytest.fixture
def mock_bot():
    """Mock Telegram bot for testing"""
    bot = AsyncMock()
    bot.session = AsyncMock()
    bot.session.close = AsyncMock()
    return bot


@pytest.fixture
def mock_message():
    """Mock Telegram message for testing"""
    message = AsyncMock()
    message.from_user.id = 12345
    message.from_user.username = "test_user"
    message.from_user.first_name = "Test"
    message.text = "Test message"
    message.answer = AsyncMock()
    message.bot.send_chat_action = AsyncMock()
    return message


@pytest.fixture
def mock_callback_query():
    """Mock Telegram callback query for testing"""
    callback = AsyncMock()
    callback.from_user.id = 12345
    callback.from_user.username = "test_user"
    callback.data = "test_callback"
    callback.message.edit_text = AsyncMock()
    callback.answer = AsyncMock()
    return callback


# Pytest markers
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "asyncio: mark test as async test")
