import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Program:
    name: str
    url: str
    institute: str
    duration: str
    language: str
    cost: str
    description: str
    directions: list[dict]
    career_prospects: list[str]
    partners: list[str]
    team: list[dict]
    admission_ways: list[str]
    faq: list[dict]
    exam_dates: list[str]
    created_at: str
    updated_at: str


@dataclass
class UserProfile:
    user_id: int
    username: str
    background: dict
    interests: list[str]
    technical_skills: list[str]
    career_goals: list[str]
    preferred_program: Optional[str]
    created_at: str
    updated_at: str


class Database:
    def __init__(self, db_path: str = "data/chatbot.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_database()

    def init_database(self):
        """Initialize database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS programs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    url TEXT NOT NULL,
                    institute TEXT,
                    duration TEXT,
                    language TEXT,
                    cost TEXT,
                    description TEXT,
                    directions TEXT,  -- JSON
                    career_prospects TEXT,  -- JSON
                    partners TEXT,  -- JSON
                    team TEXT,  -- JSON
                    admission_ways TEXT,  -- JSON
                    faq TEXT,  -- JSON
                    exam_dates TEXT,  -- JSON
                    created_at TEXT,
                    updated_at TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS user_profiles (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    background TEXT,  -- JSON
                    interests TEXT,  -- JSON
                    technical_skills TEXT,  -- JSON
                    career_goals TEXT,  -- JSON
                    preferred_program TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message TEXT,
                    response TEXT,
                    timestamp TEXT,
                    FOREIGN KEY (user_id) REFERENCES user_profiles (user_id)
                )
            """
            )

            conn.commit()

    def save_program(self, program: Program) -> bool:
        """Save program information to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO programs (
                        name, url, institute, duration, language, cost, description,
                        directions, career_prospects, partners, team, admission_ways,
                        faq, exam_dates, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        program.name,
                        program.url,
                        program.institute,
                        program.duration,
                        program.language,
                        program.cost,
                        program.description,
                        json.dumps(program.directions, ensure_ascii=False),
                        json.dumps(program.career_prospects, ensure_ascii=False),
                        json.dumps(program.partners, ensure_ascii=False),
                        json.dumps(program.team, ensure_ascii=False),
                        json.dumps(program.admission_ways, ensure_ascii=False),
                        json.dumps(program.faq, ensure_ascii=False),
                        json.dumps(program.exam_dates, ensure_ascii=False),
                        program.created_at,
                        program.updated_at,
                    ),
                )
                conn.commit()
            return True
        except Exception as e:
            print(f"Error saving program: {e}")
            return False

    def get_program(self, name: str) -> Optional[Program]:
        """Get program by name"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT * FROM programs WHERE name = ?", (name,))
                row = cursor.fetchone()
                if row:
                    return Program(
                        name=row[1],
                        url=row[2],
                        institute=row[3],
                        duration=row[4],
                        language=row[5],
                        cost=row[6],
                        description=row[7],
                        directions=json.loads(row[8]),
                        career_prospects=json.loads(row[9]),
                        partners=json.loads(row[10]),
                        team=json.loads(row[11]),
                        admission_ways=json.loads(row[12]),
                        faq=json.loads(row[13]),
                        exam_dates=json.loads(row[14]),
                        created_at=row[15],
                        updated_at=row[16],
                    )
        except Exception as e:
            print(f"Error getting program: {e}")
        return None

    def get_all_programs(self) -> list[Program]:
        """Get all programs"""
        programs = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT * FROM programs")
                for row in cursor.fetchall():
                    programs.append(
                        Program(
                            name=row[1],
                            url=row[2],
                            institute=row[3],
                            duration=row[4],
                            language=row[5],
                            cost=row[6],
                            description=row[7],
                            directions=json.loads(row[8]),
                            career_prospects=json.loads(row[9]),
                            partners=json.loads(row[10]),
                            team=json.loads(row[11]),
                            admission_ways=json.loads(row[12]),
                            faq=json.loads(row[13]),
                            exam_dates=json.loads(row[14]),
                            created_at=row[15],
                            updated_at=row[16],
                        )
                    )
        except Exception as e:
            print(f"Error getting all programs: {e}")
        return programs

    def save_user_profile(self, profile: UserProfile) -> bool:
        """Save user profile to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO user_profiles (
                        user_id, username, background, interests, technical_skills,
                        career_goals, preferred_program, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        profile.user_id,
                        profile.username,
                        json.dumps(profile.background, ensure_ascii=False),
                        json.dumps(profile.interests, ensure_ascii=False),
                        json.dumps(profile.technical_skills, ensure_ascii=False),
                        json.dumps(profile.career_goals, ensure_ascii=False),
                        profile.preferred_program,
                        profile.created_at,
                        profile.updated_at,
                    ),
                )
                conn.commit()
            return True
        except Exception as e:
            print(f"Error saving user profile: {e}")
            return False

    def get_user_profile(self, user_id: int) -> Optional[UserProfile]:
        """Get user profile by user_id"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                if row:
                    return UserProfile(
                        user_id=row[0],
                        username=row[1],
                        background=json.loads(row[2]) if row[2] else {},
                        interests=json.loads(row[3]) if row[3] else [],
                        technical_skills=json.loads(row[4]) if row[4] else [],
                        career_goals=json.loads(row[5]) if row[5] else [],
                        preferred_program=row[6],
                        created_at=row[7],
                        updated_at=row[8],
                    )
        except Exception as e:
            print(f"Error getting user profile: {e}")
        return None

    def save_conversation(self, user_id: int, message: str, response: str, timestamp: str) -> bool:
        """Save conversation to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO conversations (user_id, message, response, timestamp)
                    VALUES (?, ?, ?, ?)
                """,
                    (user_id, message, response, timestamp),
                )
                conn.commit()
            return True
        except Exception as e:
            print(f"Error saving conversation: {e}")
            return False
