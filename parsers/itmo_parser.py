import re
import time
from datetime import datetime
from typing import Optional

import requests
from bs4 import BeautifulSoup

from config import settings
from models.database import Database, Program


class ITMOParser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": settings.user_agent})
        self.db = Database()

    def parse_program_page(self, url: str) -> Optional[dict]:
        """Parse ITMO program page and extract structured data"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            # Extract program name
            program_name = self._extract_program_name(soup)

            # Extract basic info
            basic_info = self._extract_basic_info(soup)

            # Extract description
            description = self._extract_description(soup)

            # Extract directions
            directions = self._extract_directions(soup)

            # Extract career prospects
            career_prospects = self._extract_career_prospects(soup)

            # Extract partners
            partners = self._extract_partners(soup)

            # Extract team info
            team = self._extract_team(soup)

            # Extract admission ways
            admission_ways = self._extract_admission_ways(soup)

            # Extract FAQ
            faq = self._extract_faq(soup)

            # Extract exam dates
            exam_dates = self._extract_exam_dates(soup)

            return {
                "name": program_name,
                "url": url,
                "institute": basic_info.get("institute", ""),
                "duration": basic_info.get("duration", ""),
                "language": basic_info.get("language", ""),
                "cost": basic_info.get("cost", ""),
                "description": description,
                "directions": directions,
                "career_prospects": career_prospects,
                "partners": partners,
                "team": team,
                "admission_ways": admission_ways,
                "faq": faq,
                "exam_dates": exam_dates,
            }

        except Exception as e:
            print(f"Error parsing {url}: {e}")
            return None

    def _extract_program_name(self, soup: BeautifulSoup) -> str:
        """Extract program name from page"""
        h1_tag = soup.find("h1")
        if h1_tag:
            return h1_tag.get_text(strip=True)
        return ""

    def _extract_basic_info(self, soup: BeautifulSoup) -> dict:
        """Extract basic program information"""
        info = {}

        # Find institute link
        institute_link = soup.find("a", href=lambda x: x and "viewfaculty" in x)
        if institute_link:
            info["institute"] = institute_link.get_text(strip=True)

        # Extract duration, language, cost from structured data
        soup.find_all(
            "div",
            class_=lambda x: x
            and any(
                term in str(x).lower()
                for term in [
                    "duration",
                    "language",
                    "cost",
                    "форма",
                    "длительность",
                    "язык",
                    "стоимость",
                ]
            ),
        )

        # Try to find specific info in text
        page_text = soup.get_text()

        # Duration
        duration_match = re.search(r"(\d+\s*года?)", page_text)
        if duration_match:
            info["duration"] = duration_match.group(1)

        # Language
        if "русский" in page_text.lower():
            info["language"] = "русский"
        elif "english" in page_text.lower():
            info["language"] = "английский"

        # Cost
        cost_match = re.search(r"(\d+\s*\d*\s*000\s*₽)", page_text)
        if cost_match:
            info["cost"] = cost_match.group(1)

        return info

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract program description"""
        # Look for program description section
        desc_section = soup.find("section", {"id": "about"}) or soup.find(
            "div", string=lambda x: x and "о программе" in x.lower()
        )

        if desc_section:
            # Find the next div with text content
            content_div = desc_section.find_next("div")
            if content_div:
                return content_div.get_text(strip=True, separator=" ")

        # Fallback: look for any large text block
        text_blocks = soup.find_all("div", string=lambda x: x and len(str(x)) > 200)
        if text_blocks:
            return text_blocks[0].get_text(strip=True, separator=" ")[:1000]

        return ""

    def _extract_directions(self, soup: BeautifulSoup) -> list[dict]:
        """Extract study directions"""
        directions = []

        # Look for directions section
        direction_headers = soup.find_all(
            "h5",
            string=lambda x: x
            and any(
                term in str(x).lower()
                for term in ["информатика", "инноватика", "инфокоммуникационные", "математическое"]
            ),
        )

        for header in direction_headers:
            direction_info = {
                "name": header.get_text(strip=True),
                "code": "",
                "budget_places": 0,
                "target_places": 0,
                "contract_places": 0,
            }

            # Try to find numbers near the direction
            parent = header.find_parent()
            if parent:
                text = parent.get_text()

                # Extract budget places
                budget_match = re.search(r"(\d+)\s*бюджетных", text)
                if budget_match:
                    direction_info["budget_places"] = int(budget_match.group(1))

                # Extract target places
                target_match = re.search(r"(\d+)\s*целевая", text)
                if target_match:
                    direction_info["target_places"] = int(target_match.group(1))

                # Extract contract places
                contract_match = re.search(r"(\d+)\s*контрактных", text)
                if contract_match:
                    direction_info["contract_places"] = int(contract_match.group(1))

                # Extract direction code
                code_match = re.search(r"(\d{2}\.\d{2}\.\d{2})", text)
                if code_match:
                    direction_info["code"] = code_match.group(1)

            directions.append(direction_info)

        return directions

    def _extract_career_prospects(self, soup: BeautifulSoup) -> list[str]:
        """Extract career prospects"""
        prospects = []

        # Look for career section
        career_section = soup.find("section", string=lambda x: x and "карьера" in str(x).lower())
        if not career_section:
            career_section = soup.find("div", string=lambda x: x and "карьера" in str(x).lower())

        if career_section:
            # Find career-related text
            career_text = career_section.find_next("div")
            if career_text:
                text = career_text.get_text()
                # Extract roles mentioned
                roles = re.findall(
                    r"[–-]\s*([A-Za-z\s]+(?:Engineer|Manager|Developer|Analyst|Lead))", text
                )
                prospects.extend([role.strip() for role in roles])

        # Fallback: search for common job titles in text
        page_text = soup.get_text()
        common_roles = [
            "ML Engineer",
            "Data Engineer",
            "AI Product Developer",
            "Data Analyst",
            "AI Product Manager",
            "AI Project Manager",
            "Product Data Analyst",
            "AI Product Lead",
        ]

        for role in common_roles:
            if role in page_text:
                prospects.append(role)

        return list(set(prospects))

    def _extract_partners(self, soup: BeautifulSoup) -> list[str]:
        """Extract program partners"""
        partners = []

        # Look for partners section
        partners_section = soup.find("div", class_="partners")
        if partners_section:
            # Find all images in partners section
            partner_imgs = partners_section.find_all("img")
            for img in partner_imgs:
                alt_text = img.get("alt", "")
                if alt_text:
                    partners.append(alt_text)

        # Also look for partner images anywhere with alt text
        all_imgs = soup.find_all("img", alt=True)
        for img in all_imgs:
            alt_text = img.get("alt", "")
            src = img.get("src", "")

            # Check if it's a partner logo by alt text or src
            if any(
                company in alt_text for company in ["X5 Group", "Ozon Bank", "Альфа-Банк", "МТС"]
            ) or any(
                company.lower().replace(" ", "").replace("-", "") in src.lower()
                for company in ["x5group", "ozonbank", "alphabank", "mts"]
            ):
                partners.append(alt_text)

        # Also look for well-known company names in text
        companies = [
            "X5 Group",
            "Ozon Bank",
            "МТС",
            "Sber AI",
            "Норникель",
            "Napoleon IT",
            "Genotek",
            "Raft",
            "AIRI",
            "DeepPavlov",
            "Яндекс",
            "Газпромбанк",
            "Альфа-Банк",
            "Tinkoff",
            "Wildberries",
            "Huawei",
        ]

        page_text = soup.get_text()
        for company in companies:
            if company in page_text:
                partners.append(company)

        return list(set(partners))

    def _extract_team(self, soup: BeautifulSoup) -> list[dict]:
        """Extract team information"""
        team = []

        # Look for team section
        team_section = soup.find("div", string=lambda x: x and "команда" in str(x).lower())
        if team_section:
            # Find team member cards
            team_cards = team_section.find_next_siblings("div")

            for card in team_cards[:5]:  # Limit to first 5 members
                name_tag = card.find("h3") or card.find("h4") or card.find("strong")
                if name_tag:
                    member_info = {
                        "name": name_tag.get_text(strip=True),
                        "position": "",
                        "description": "",
                    }

                    # Try to extract position
                    text = card.get_text()
                    if "руководитель" in text.lower():
                        member_info["position"] = "Руководитель программы"
                    elif "доцент" in text.lower():
                        member_info["position"] = "Доцент"
                    elif "преподаватель" in text.lower():
                        member_info["position"] = "Преподаватель"

                    team.append(member_info)

        return team

    def _extract_admission_ways(self, soup: BeautifulSoup) -> list[str]:
        """Extract ways to apply"""
        ways = []

        # Look for admission section
        admission_sections = soup.find_all(
            "h5",
            string=lambda x: x
            and any(
                term in str(x).lower() for term in ["экзамен", "конкурс", "портфолио", "олимпиада"]
            ),
        )

        for section in admission_sections:
            way_name = section.get_text(strip=True)
            ways.append(way_name)

        return ways

    def _extract_faq(self, soup: BeautifulSoup) -> list[dict]:
        """Extract FAQ"""
        faq = []

        # Look for FAQ section
        faq_section = soup.find("section", string=lambda x: x and "вопрос" in str(x).lower())
        if faq_section:
            questions = faq_section.find_all("h5")

            for q in questions:
                question_text = q.get_text(strip=True)
                # Try to find answer
                answer_elem = q.find_next_sibling("div") or q.find_next("p")
                answer_text = answer_elem.get_text(strip=True) if answer_elem else ""

                faq.append(
                    {"question": question_text, "answer": answer_text[:500]}  # Limit answer length
                )

        return faq

    def _extract_exam_dates(self, soup: BeautifulSoup) -> list[str]:
        """Extract exam dates"""
        dates = []

        # Look for date elements
        date_elements = soup.find_all(
            "div", string=lambda x: x and re.search(r"\d{2}\.\d{2}\.\d{4}", str(x))
        )

        for elem in date_elements:
            date_text = elem.get_text(strip=True)
            dates.append(date_text)

        return dates

    def parse_and_save_programs(self):
        """Parse both program pages and save to database"""
        urls = [
            "https://abit.itmo.ru/program/master/ai",
            "https://abit.itmo.ru/program/master/ai_product",
        ]

        for url in urls:
            print(f"Parsing {url}...")
            program_data = self.parse_program_page(url)

            if program_data:
                now = datetime.now().isoformat()
                program = Program(
                    name=program_data["name"],
                    url=program_data["url"],
                    institute=program_data["institute"],
                    duration=program_data["duration"],
                    language=program_data["language"],
                    cost=program_data["cost"],
                    description=program_data["description"],
                    directions=program_data["directions"],
                    career_prospects=program_data["career_prospects"],
                    partners=program_data["partners"],
                    team=program_data["team"],
                    admission_ways=program_data["admission_ways"],
                    faq=program_data["faq"],
                    exam_dates=program_data["exam_dates"],
                    created_at=now,
                    updated_at=now,
                )

                success = self.db.save_program(program)
                if success:
                    print(f"Successfully saved program: {program.name}")
                else:
                    print(f"Failed to save program: {program.name}")

            # Respect rate limiting
            time.sleep(settings.request_delay)


if __name__ == "__main__":
    parser = ITMOParser()
    parser.parse_and_save_programs()
