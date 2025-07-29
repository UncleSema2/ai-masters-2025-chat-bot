"""
Unit tests for database module
"""

from datetime import datetime
from typing import Any

import pytest

from models.database import Database, Program, UserProfile


@pytest.mark.unit
class TestDatabase:
    """Test Database class"""

    def test_database_initialization(self, temp_db: Database):
        """Test database initialization creates tables"""
        # Check if tables exist by trying to query them
        with temp_db.db_path.open():
            pass  # Database file should exist

        # Try to insert and retrieve data to verify tables exist
        test_program = Program(
            name="Test Program",
            url="https://test.com",
            institute="Test Institute",
            duration="2 years",
            language="russian",
            cost="100000",
            description="Test description",
            directions=[],
            career_prospects=[],
            partners=[],
            team=[],
            admission_ways=[],
            faq=[],
            exam_dates=[],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

        success = temp_db.save_program(test_program)
        assert success is True

    def test_save_program(self, temp_db: Database, sample_program: Program):
        """Test saving program to database"""
        success = temp_db.save_program(sample_program)
        assert success is True

        # Verify program was saved
        retrieved_program = temp_db.get_program(sample_program.name)
        assert retrieved_program is not None
        assert retrieved_program.name == sample_program.name
        assert retrieved_program.url == sample_program.url
        assert retrieved_program.institute == sample_program.institute

    def test_save_program_duplicate(self, temp_db: Database, sample_program: Program):
        """Test saving duplicate program updates existing one"""
        # Save original program
        success = temp_db.save_program(sample_program)
        assert success is True

        # Modify and save again
        sample_program.description = "Updated description"
        sample_program.updated_at = datetime.now().isoformat()

        success = temp_db.save_program(sample_program)
        assert success is True

        # Verify program was updated
        retrieved_program = temp_db.get_program(sample_program.name)
        assert retrieved_program is not None
        assert retrieved_program.description == "Updated description"

    def test_get_program_exists(self, temp_db: Database, sample_program: Program):
        """Test retrieving existing program"""
        temp_db.save_program(sample_program)

        retrieved_program = temp_db.get_program(sample_program.name)
        assert retrieved_program is not None
        assert retrieved_program.name == sample_program.name
        assert retrieved_program.directions == sample_program.directions
        assert retrieved_program.career_prospects == sample_program.career_prospects

    def test_get_program_not_exists(self, temp_db: Database):
        """Test retrieving non-existent program"""
        retrieved_program = temp_db.get_program("Non-existent Program")
        assert retrieved_program is None

    def test_get_all_programs_empty(self, temp_db: Database):
        """Test getting programs from empty database"""
        programs = temp_db.get_all_programs()
        assert programs == []

    def test_get_all_programs_with_data(self, temp_db: Database, sample_program: Program):
        """Test getting programs with data in database"""
        temp_db.save_program(sample_program)

        # Create second program
        program2 = Program(
            name="Second Program",
            url="https://test2.com",
            institute="Test Institute 2",
            duration="2 years",
            language="english",
            cost="200000",
            description="Second test description",
            directions=[],
            career_prospects=["Manager"],
            partners=["Partner1"],
            team=[],
            admission_ways=[],
            faq=[],
            exam_dates=[],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        temp_db.save_program(program2)

        programs = temp_db.get_all_programs()
        assert len(programs) == 2
        program_names = [p.name for p in programs]
        assert sample_program.name in program_names
        assert program2.name in program_names

    def test_save_user_profile(self, temp_db: Database, sample_user_profile: UserProfile):
        """Test saving user profile"""
        success = temp_db.save_user_profile(sample_user_profile)
        assert success is True

        # Verify profile was saved
        retrieved_profile = temp_db.get_user_profile(sample_user_profile.user_id)
        assert retrieved_profile is not None
        assert retrieved_profile.user_id == sample_user_profile.user_id
        assert retrieved_profile.username == sample_user_profile.username
        assert retrieved_profile.interests == sample_user_profile.interests

    def test_save_user_profile_update(self, temp_db: Database, sample_user_profile: UserProfile):
        """Test updating existing user profile"""
        # Save original profile
        success = temp_db.save_user_profile(sample_user_profile)
        assert success is True

        # Update profile
        sample_user_profile.interests = ["new interest"]
        sample_user_profile.updated_at = datetime.now().isoformat()

        success = temp_db.save_user_profile(sample_user_profile)
        assert success is True

        # Verify profile was updated
        retrieved_profile = temp_db.get_user_profile(sample_user_profile.user_id)
        assert retrieved_profile is not None
        assert retrieved_profile.interests == ["new interest"]

    def test_get_user_profile_exists(self, temp_db: Database, sample_user_profile: UserProfile):
        """Test retrieving existing user profile"""
        temp_db.save_user_profile(sample_user_profile)

        retrieved_profile = temp_db.get_user_profile(sample_user_profile.user_id)
        assert retrieved_profile is not None
        assert retrieved_profile.user_id == sample_user_profile.user_id
        assert retrieved_profile.technical_skills == sample_user_profile.technical_skills
        assert retrieved_profile.career_goals == sample_user_profile.career_goals

    def test_get_user_profile_not_exists(self, temp_db: Database):
        """Test retrieving non-existent user profile"""
        retrieved_profile = temp_db.get_user_profile(99999)
        assert retrieved_profile is None

    def test_save_conversation(self, temp_db: Database):
        """Test saving conversation"""
        user_id = 12345
        message = "Test question"
        response = "Test response"
        timestamp = datetime.now().isoformat()

        success = temp_db.save_conversation(user_id, message, response, timestamp)
        assert success is True

    def test_complex_program_data(self, temp_db: Database):
        """Test saving program with complex data structures"""
        complex_program = Program(
            name="Complex Program",
            url="https://complex.com",
            institute="Complex Institute",
            duration="2 years",
            language="russian",
            cost="500000",
            description="Complex description with специальные символы and emojis 🚀",
            directions=[
                {
                    "name": "Сложное направление",
                    "code": "01.02.03",
                    "budget_places": 25,
                    "target_places": 5,
                    "contract_places": 30,
                },
                {
                    "name": "Another Direction",
                    "code": "04.05.06",
                    "budget_places": 15,
                    "target_places": 2,
                    "contract_places": 20,
                },
            ],
            career_prospects=["AI Engineer", "Data Scientist", "ML Researcher"],
            partners=["Компания А", "Company B", "Организация В"],
            team=[
                {
                    "name": "Иван Иванович Иванов",
                    "position": "Профессор",
                    "description": "Доктор наук",
                }
            ],
            admission_ways=["Экзамен", "Портфолио", "Олимпиада"],
            faq=[{"question": "Сложный вопрос?", "answer": "Сложный ответ с деталями..."}],
            exam_dates=["2025-08-01", "2025-08-15"],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

        success = temp_db.save_program(complex_program)
        assert success is True

        retrieved_program = temp_db.get_program(complex_program.name)
        assert retrieved_program is not None
        assert len(retrieved_program.directions) == 2
        assert len(retrieved_program.career_prospects) == 3
        assert len(retrieved_program.partners) == 3
        assert retrieved_program.directions[0]["name"] == "Сложное направление"


@pytest.mark.unit
class TestProgram:
    """Test Program dataclass"""

    def test_program_creation(self, sample_program_data: dict[str, Any]):
        """Test creating Program instance"""
        program = Program(**sample_program_data)
        assert program.name == sample_program_data["name"]
        assert program.url == sample_program_data["url"]
        assert program.directions == sample_program_data["directions"]

    def test_program_with_minimal_data(self):
        """Test creating Program with minimal required data"""
        minimal_data = {
            "name": "Minimal Program",
            "url": "https://minimal.com",
            "institute": "",
            "duration": "",
            "language": "",
            "cost": "",
            "description": "",
            "directions": [],
            "career_prospects": [],
            "partners": [],
            "team": [],
            "admission_ways": [],
            "faq": [],
            "exam_dates": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        program = Program(**minimal_data)
        assert program.name == "Minimal Program"
        assert program.directions == []
        assert program.career_prospects == []


@pytest.mark.unit
class TestUserProfile:
    """Test UserProfile dataclass"""

    def test_user_profile_creation(self, sample_user_profile: UserProfile):
        """Test creating UserProfile instance"""
        assert sample_user_profile.user_id == 12345
        assert sample_user_profile.username == "test_user"
        assert len(sample_user_profile.interests) == 3
        assert len(sample_user_profile.technical_skills) == 4

    def test_user_profile_with_empty_lists(self):
        """Test creating UserProfile with empty lists"""
        profile = UserProfile(
            user_id=54321,
            username="empty_user",
            background={},
            interests=[],
            technical_skills=[],
            career_goals=[],
            preferred_program=None,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

        assert profile.user_id == 54321
        assert profile.interests == []
        assert profile.technical_skills == []
        assert profile.background == {}
