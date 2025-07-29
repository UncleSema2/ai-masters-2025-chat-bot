"""
Unit tests for ITMO parser module
"""

from unittest.mock import MagicMock, patch

import pytest

from parsers.itmo_parser import ITMOParser


@pytest.mark.unit
class TestITMOParser:
    """Test ITMOParser class"""

    def test_parser_initialization(self):
        """Test parser initialization"""
        with patch("parsers.itmo_parser.Database"):
            parser = ITMOParser()
            assert parser.session is not None
            assert parser.db is not None

    def test_extract_program_name(self, sample_html_ai_program):
        """Test extracting program name from HTML"""
        with patch("parsers.itmo_parser.Database"):
            parser = ITMOParser()

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(sample_html_ai_program, "html.parser")

        program_name = parser._extract_program_name(soup)
        assert program_name == "Искусственный интеллект"

    def test_extract_program_name_no_h1(self):
        """Test extracting program name when no h1 tag"""
        with patch("parsers.itmo_parser.Database"):
            parser = ITMOParser()

        from bs4 import BeautifulSoup

        soup = BeautifulSoup("<html><body>No title</body></html>", "html.parser")

        program_name = parser._extract_program_name(soup)
        assert program_name == ""

    def test_extract_basic_info(self, sample_html_ai_program):
        """Test extracting basic program information"""
        with patch("parsers.itmo_parser.Database"):
            parser = ITMOParser()

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(sample_html_ai_program, "html.parser")

        basic_info = parser._extract_basic_info(soup)

        assert basic_info["duration"] == "2 года"
        assert basic_info["language"] == "русский"
        assert basic_info["cost"] == "599 000 ₽"

    def test_extract_basic_info_empty(self):
        """Test extracting basic info from empty HTML"""
        with patch("parsers.itmo_parser.Database"):
            parser = ITMOParser()

        from bs4 import BeautifulSoup

        soup = BeautifulSoup("<html><body></body></html>", "html.parser")

        basic_info = parser._extract_basic_info(soup)
        assert isinstance(basic_info, dict)

    def test_extract_description(self, sample_html_ai_program):
        """Test extracting program description"""
        with patch("parsers.itmo_parser.Database"):
            parser = ITMOParser()

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(sample_html_ai_program, "html.parser")

        description = parser._extract_description(soup)

        assert "Создавайте AI-продукты и технологии" in description
        assert "проектный подход" in description

    def test_extract_description_no_about_section(self):
        """Test extracting description when no about section"""
        with patch("parsers.itmo_parser.Database"):
            parser = ITMOParser()

        from bs4 import BeautifulSoup

        soup = BeautifulSoup("<html><body><div>Short text</div></body></html>", "html.parser")

        description = parser._extract_description(soup)
        assert description == ""

    def test_extract_directions(self, sample_html_ai_program):
        """Test extracting study directions"""
        with patch("parsers.itmo_parser.Database"):
            parser = ITMOParser()

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(sample_html_ai_program, "html.parser")

        directions = parser._extract_directions(soup)

        assert len(directions) == 1
        assert directions[0]["name"] == "Информатика и вычислительная техника"
        assert directions[0]["code"] == "09.04.01"
        assert directions[0]["budget_places"] == 51
        assert directions[0]["target_places"] == 4
        assert directions[0]["contract_places"] == 55

    def test_extract_directions_empty(self):
        """Test extracting directions from empty HTML"""
        with patch("parsers.itmo_parser.Database"):
            parser = ITMOParser()

        from bs4 import BeautifulSoup

        soup = BeautifulSoup("<html><body></body></html>", "html.parser")

        directions = parser._extract_directions(soup)
        assert directions == []

    def test_extract_career_prospects(self, sample_html_ai_program):
        """Test extracting career prospects"""
        with patch("parsers.itmo_parser.Database"):
            parser = ITMOParser()

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(sample_html_ai_program, "html.parser")

        prospects = parser._extract_career_prospects(soup)

        assert "ML Engineer" in prospects
        assert "Data Engineer" in prospects

    def test_extract_career_prospects_empty(self):
        """Test extracting career prospects from empty HTML"""
        with patch("parsers.itmo_parser.Database"):
            parser = ITMOParser()

        from bs4 import BeautifulSoup

        soup = BeautifulSoup("<html><body></body></html>", "html.parser")

        prospects = parser._extract_career_prospects(soup)
        assert isinstance(prospects, list)

    def test_extract_partners(self, sample_html_ai_program):
        """Test extracting program partners"""
        with patch("parsers.itmo_parser.Database"):
            parser = ITMOParser()

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(sample_html_ai_program, "html.parser")

        partners = parser._extract_partners(soup)

        assert "X5 Group" in partners
        assert "Ozon Bank" in partners

    def test_extract_partners_empty(self):
        """Test extracting partners from empty HTML"""
        with patch("parsers.itmo_parser.Database"):
            parser = ITMOParser()

        from bs4 import BeautifulSoup

        soup = BeautifulSoup("<html><body></body></html>", "html.parser")

        partners = parser._extract_partners(soup)
        assert isinstance(partners, list)

    def test_extract_team_empty(self):
        """Test extracting team from empty HTML"""
        with patch("parsers.itmo_parser.Database"):
            parser = ITMOParser()

        from bs4 import BeautifulSoup

        soup = BeautifulSoup("<html><body></body></html>", "html.parser")

        team = parser._extract_team(soup)
        assert team == []

    def test_extract_admission_ways_empty(self):
        """Test extracting admission ways from empty HTML"""
        with patch("parsers.itmo_parser.Database"):
            parser = ITMOParser()

        from bs4 import BeautifulSoup

        soup = BeautifulSoup("<html><body></body></html>", "html.parser")

        ways = parser._extract_admission_ways(soup)
        assert ways == []

    def test_extract_faq_empty(self):
        """Test extracting FAQ from empty HTML"""
        with patch("parsers.itmo_parser.Database"):
            parser = ITMOParser()

        from bs4 import BeautifulSoup

        soup = BeautifulSoup("<html><body></body></html>", "html.parser")

        faq = parser._extract_faq(soup)
        assert faq == []

    def test_extract_exam_dates(self, sample_html_ai_program):
        """Test extracting exam dates"""
        with patch("parsers.itmo_parser.Database"):
            parser = ITMOParser()

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(sample_html_ai_program, "html.parser")

        dates = parser._extract_exam_dates(soup)

        assert "29.07.2025, 11:00" in dates
        assert "31.07.2025, 11:00" in dates

    def test_extract_exam_dates_empty(self):
        """Test extracting exam dates from empty HTML"""
        with patch("parsers.itmo_parser.Database"):
            parser = ITMOParser()

        from bs4 import BeautifulSoup

        soup = BeautifulSoup("<html><body></body></html>", "html.parser")

        dates = parser._extract_exam_dates(soup)
        assert dates == []

    @patch("parsers.itmo_parser.requests.Session.get")
    def test_parse_program_page_success(
        self, mock_get, sample_html_ai_program, mock_requests_response
    ):
        """Test successful parsing of program page"""
        # Mock successful HTTP response
        mock_get.return_value = mock_requests_response(sample_html_ai_program)

        with patch("parsers.itmo_parser.Database"):
            parser = ITMOParser()

        url = "https://abit.itmo.ru/program/master/ai"
        result = parser.parse_program_page(url)

        assert result is not None
        assert result["name"] == "Искусственный интеллект"
        assert result["url"] == url
        assert len(result["directions"]) == 1
        assert "ML Engineer" in result["career_prospects"]

    @patch("parsers.itmo_parser.requests.Session.get")
    def test_parse_program_page_http_error(self, mock_get):
        """Test parsing with HTTP error"""
        # Mock HTTP error
        mock_get.side_effect = Exception("HTTP Error")

        with patch("parsers.itmo_parser.Database"):
            parser = ITMOParser()

        url = "https://abit.itmo.ru/program/master/ai"
        result = parser.parse_program_page(url)

        assert result is None

    @patch("parsers.itmo_parser.requests.Session.get")
    @patch("parsers.itmo_parser.time.sleep")
    def test_parse_and_save_programs(
        self,
        mock_sleep,
        mock_get,
        sample_html_ai_program,
        sample_html_ai_product,
        mock_requests_response,
        temp_db,
    ):
        """Test parsing and saving both programs"""

        # Mock HTTP responses for both URLs
        def side_effect(url):
            if "ai_product" in url:
                return mock_requests_response(sample_html_ai_product)
            else:
                return mock_requests_response(sample_html_ai_program)

        mock_get.side_effect = side_effect

        # Use real database for this test
        parser = ITMOParser()
        parser.db = temp_db

        parser.parse_and_save_programs()

        # Verify both programs were saved
        programs = temp_db.get_all_programs()
        assert len(programs) == 2

        program_names = [p.name for p in programs]
        assert "Искусственный интеллект" in program_names
        assert "Управление ИИ-продуктами/AI Product" in program_names

        # Verify sleep was called for rate limiting
        assert mock_sleep.call_count == 2

    @patch("parsers.itmo_parser.requests.Session.get")
    def test_parse_and_save_programs_with_error(self, mock_get, temp_db):
        """Test parsing with one successful and one failed request"""

        # Mock one success and one failure
        def side_effect(url):
            if "ai_product" in url:
                raise Exception("Network error")
            else:
                mock_response = MagicMock()
                mock_response.content = b"<html><h1>Test</h1></html>"
                mock_response.raise_for_status.return_value = None
                return mock_response

        mock_get.side_effect = side_effect

        parser = ITMOParser()
        parser.db = temp_db

        # Should not raise exception, just handle errors gracefully
        parser.parse_and_save_programs()

        # Verify at least one program attempt was made
        assert mock_get.call_count == 2

    def test_ai_product_program_parsing(self, sample_html_ai_product):
        """Test parsing AI Product program specifically"""
        with patch("parsers.itmo_parser.Database"):
            parser = ITMOParser()

        from bs4 import BeautifulSoup

        soup = BeautifulSoup(sample_html_ai_product, "html.parser")

        # Test program name
        name = parser._extract_program_name(soup)
        assert name == "Управление ИИ-продуктами/AI Product"

        # Test directions
        directions = parser._extract_directions(soup)
        assert len(directions) == 1
        assert (
            directions[0]["name"]
            == "Математическое обеспечение и администрирование информационных систем"
        )
        assert directions[0]["code"] == "02.04.03"
        assert directions[0]["budget_places"] == 14
        assert directions[0]["contract_places"] == 50

        # Test career prospects
        prospects = parser._extract_career_prospects(soup)
        assert "AI Product Manager" in prospects
        assert "AI Project Manager" in prospects

        # Test partners
        partners = parser._extract_partners(soup)
        assert "Альфа-Банк" in partners
