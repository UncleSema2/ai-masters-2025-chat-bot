from datetime import datetime

import openai

from config import settings
from models.database import Database, UserProfile


class AIAssistant:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.db = Database()

        # System prompt for the AI assistant
        self.system_prompt = """
Ты - эксперт-консультант по магистерским программам ИТМО в области искусственного интеллекта.
Твоя задача - помочь абитуриентам выбрать подходящую программу и спланировать обучение.

У тебя есть доступ к информации о двух программах:
1. "Искусственный интеллект" - техническая программа с фокусом на ML Engineering, Data Engineering, AI Product Development
2. "Управление ИИ-продуктами/AI Product" - продуктовая программа с фокусом на AI Product Management

ВАЖНЫЕ ПРАВИЛА:
- Отвечай ТОЛЬКО на вопросы, связанные с этими двумя магистерскими программами ИТМО
- Если вопрос не касается обучения в данных магистратурах, вежливо перенаправь пользователя к релевантной теме
- Используй только проверенную информацию из базы данных
- Давай конкретные и практичные рекомендации
- Учитывай бэкграунд и цели абитуриента при составлении рекомендаций

Формат ответов:
- Структурированные и информативные
- С конкретными примерами
- С учетом карьерных перспектив
- С рекомендациями по выборным дисциплинам (если применимо)
"""

    def get_programs_context(self) -> str:
        """Get context about all programs for AI assistant"""
        programs = self.db.get_all_programs()
        context = ""

        for program in programs:
            context += f"""
ПРОГРАММА: {program.name}
URL: {program.url}
Институт: {program.institute}
Длительность: {program.duration}
Язык обучения: {program.language}
Стоимость: {program.cost}

Описание: {program.description}

Направления подготовки:
{self._format_directions(program.directions)}

Карьерные перспективы:
{', '.join(program.career_prospects)}

Партнеры:
{', '.join(program.partners)}

Способы поступления:
{', '.join(program.admission_ways)}

Даты экзаменов:
{', '.join(program.exam_dates)}

FAQ:
{self._format_faq(program.faq)}

---
"""
        return context

    def _format_directions(self, directions: list[dict]) -> str:
        """Format directions for context"""
        if not directions:
            return "Информация о направлениях не найдена"

        result = ""
        for direction in directions:
            result += f"- {direction.get('name', 'N/A')} ({direction.get('code', 'N/A')})\n"
            result += f"  Бюджет: {direction.get('budget_places', 0)}, "
            result += f"Целевые: {direction.get('target_places', 0)}, "
            result += f"Контракт: {direction.get('contract_places', 0)}\n"
        return result

    def _format_faq(self, faq: list[dict]) -> str:
        """Format FAQ for context"""
        if not faq:
            return "FAQ не найден"

        result = ""
        for qa in faq[:5]:  # Limit to first 5 FAQ items
            result += f"Q: {qa.get('question', '')}\n"
            result += f"A: {qa.get('answer', '')}\n\n"
        return result

    def is_relevant_question(self, question: str) -> bool:
        """Check if question is relevant to ITMO AI master programs"""
        irrelevant_keywords = [
            "погода",
            "спорт",
            "политика",
            "новости",
            "рецепт",
            "фильм",
            "музыка",
            "игра",
            "автомобиль",
            "путешествие",
            "здоровье",
            "футбол",
            "борщ",
            "приготовить",
            "купить",
            "телефон",
        ]

        relevant_keywords = [
            "итмо",
            "магистр",
            "поступление",
            "обучение",
            "программа",
            "программы",
            "искусственный интеллект",
            "машинное обучение",
            "ai",
            "ml",
            "продукт",
            "карьера",
            "экзамен",
            "документы",
            "бюджет",
            "контракт",
            "стипендия",
            "общежитие",
            "университет",
            "вуз",
            "отличаются",
            "разница",
            "сравнить",
            "подходит",
            "требования",
            "стоимость",
            "стоит",
            "перспективы",
            "доступны",
        ]

        question_lower = question.lower()

        # Check for irrelevant keywords first (more strict)
        for keyword in irrelevant_keywords:
            if keyword in question_lower:
                return False

        # Check for relevant keywords
        for keyword in relevant_keywords:
            if keyword in question_lower:
                return True

        # If no clear keywords and question is too short, it's likely irrelevant
        if len(question_lower.split()) <= 2:
            return False

        # For longer questions without clear keywords, assume relevant
        # This handles neutral academic questions like "Расскажите подробнее о возможностях данного направления"
        if len(question_lower.split()) > 3:
            return True

        return False

    async def get_response(self, user_message: str, user_id: int) -> str:
        """Generate AI response to user message"""
        try:
            # Check if question is relevant
            if not self.is_relevant_question(user_message):
                return """
Я специализируюсь только на вопросах, связанных с магистерскими программами ИТМО в области искусственного интеллекта:
• "Искусственный интеллект"
• "Управление ИИ-продуктами/AI Product"

Пожалуйста, задайте вопрос о поступлении, обучении, карьерных перспективах или других аспектах этих программ.
"""

            # Get user profile for personalized recommendations
            user_profile = self.db.get_user_profile(user_id)
            profile_context = ""

            if user_profile:
                profile_context = f"""
ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ:
Интересы: {', '.join(user_profile.interests)}
Технические навыки: {', '.join(user_profile.technical_skills)}
Карьерные цели: {', '.join(user_profile.career_goals)}
Предпочитаемая программа: {user_profile.preferred_program or 'не указана'}
"""

            # Get programs context
            programs_context = self.get_programs_context()

            # Construct the full prompt
            messages = [
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": f"""
{programs_context}

{profile_context}

ВОПРОС ПОЛЬЗОВАТЕЛЯ: {user_message}

Пожалуйста, дай подробный и полезный ответ, основанный на предоставленной информации о программах.
""",
                },
            ]

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, max_tokens=1500, temperature=0.7
            )

            ai_response = response.choices[0].message.content.strip()

            # Save conversation to database
            timestamp = datetime.now().isoformat()
            self.db.save_conversation(user_id, user_message, ai_response, timestamp)

            return ai_response

        except Exception as e:
            print(f"Error getting AI response: {e}")
            return "Извините, произошла ошибка при обработке вашего запроса. Попробуйте еще раз."

    def generate_program_recommendation(self, user_profile: UserProfile) -> str:
        """Generate personalized program recommendation"""
        try:
            programs_context = self.get_programs_context()

            messages = [
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": f"""
{programs_context}

ПРОФИЛЬ АБИТУРИЕНТА:
Интересы: {', '.join(user_profile.interests)}
Технические навыки: {', '.join(user_profile.technical_skills)}
Карьерные цели: {', '.join(user_profile.career_goals)}
Дополнительная информация: {user_profile.background}

ЗАДАЧА: Проанализируй профиль абитуриента и дай детальную рекомендацию:
1. Какая программа лучше подходит и почему
2. Конкретные преимущества выбранной программы для данного профиля
3. Рекомендации по подготовке к поступлению
4. Suggested траектория обучения (какие курсы/проекты выбрать)
5. Карьерные перспективы после окончания

Будь конкретным и обоснованным в своих рекомендациях.
""",
                },
            ]

            response = self.client.chat.completions.create(
                model=self.model, messages=messages, max_tokens=2000, temperature=0.6
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error generating recommendation: {e}")
            return "Не удалось сгенерировать рекомендацию. Попробуйте позже."

    def compare_programs(self) -> str:
        """Generate detailed comparison between programs"""
        try:
            programs_context = self.get_programs_context()

            messages = [
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": f"""
{programs_context}

ЗАДАЧА: Создай подробное сравнение двух программ магистратуры ИТМО:

Сравни программы по следующим критериям:
1. Фокус и специализация
2. Карьерные возможности
3. Партнеры и проекты
4. Направления подготовки и количество мест
5. Способы поступления
6. Для кого подходит каждая программа

Представь информацию в структурированном виде, выделяя ключевые различия.
""",
                },
            ]

            response = self.client.chat.completions.create(
                model=self.model, messages=messages, max_tokens=2000, temperature=0.5
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error comparing programs: {e}")
            return "Не удалось выполнить сравнение программ. Попробуйте позже."

    def generate_admission_guide(self) -> str:
        """Generate comprehensive admission guide"""
        try:
            programs_context = self.get_programs_context()

            messages = [
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": f"""
{programs_context}

ЗАДАЧА: Создай подробный гид по поступлению на программы магистратуры ИТМО по ИИ.

Включи следующую информацию:
1. Все способы поступления (экзамены, конкурсы, портфолио и т.д.)
2. Даты и сроки
3. Требования и документы
4. Советы по подготовке к каждому способу поступления
5. Количество мест на каждом направлении
6. Стоимость обучения и возможности получения стипендий

Структурируй информацию так, чтобы она была максимально полезна для абитуриента.
""",
                },
            ]

            response = self.client.chat.completions.create(
                model=self.model, messages=messages, max_tokens=2000, temperature=0.5
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Error generating admission guide: {e}")
            return "Не удалось создать гид по поступлению. Попробуйте позже."
