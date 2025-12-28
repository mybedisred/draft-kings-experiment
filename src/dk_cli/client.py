import asyncio
import re
from datetime import datetime
from typing import List, Optional

from playwright.async_api import async_playwright, Browser, Page

from .models import NFLGame, Team, BettingLines, MoneyLine, Spread, Total


NFL_URL = "https://sportsbook.draftkings.com/leagues/football/nfl"


class DraftKingsClient:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self._browser: Optional[Browser] = None
        self._playwright = None

    async def __aenter__(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.headless)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def fetch_nfl_games(self) -> List[NFLGame]:
        """Fetch all NFL games with betting lines from DraftKings."""
        if not self._browser:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        page = await self._browser.new_page()
        try:
            # Use 'load' instead of 'networkidle' - DK has constant websocket activity
            await page.goto(NFL_URL, wait_until="load", timeout=60000)

            # Wait for betting content to appear
            try:
                await page.wait_for_selector("[class*='sportsbook-table'], [class*='parlay-card'], [class*='event-cell']", timeout=20000)
            except:
                # If no betting tables, page might still have data in other format
                await asyncio.sleep(3)

            games = await self._parse_games(page)
            return games
        finally:
            await page.close()

    async def _parse_games(self, page: Page) -> List[NFLGame]:
        """Parse game data from the page."""
        games = []

        # Find all event rows (each game)
        event_rows = await page.query_selector_all("table.sportsbook-table tbody tr")

        if not event_rows:
            # Try alternative selector pattern
            event_rows = await page.query_selector_all("[class*='sportsbook-event-accordion'] [class*='event']")

        # DraftKings displays games in pairs (away team row, home team row)
        # Let's get all the data from the page's JavaScript state instead
        games = await self._parse_from_page_data(page)

        return games

    async def _parse_from_page_data(self, page: Page) -> List[NFLGame]:
        """Extract game data from page's embedded JSON or DOM structure."""
        games = []

        # DraftKings uses cb-* (component builder) classes
        # Each game is in a cb-static-parlay__content--inner or similar container
        game_cards = await page.query_selector_all("[class*='cb-static-parlay__content']")

        if not game_cards:
            # Try alternative selectors
            game_cards = await page.query_selector_all("[class*='parlay-card-10']")

        for card in game_cards:
            try:
                game = await self._parse_cb_game_card(card)
                if game:
                    games.append(game)
            except Exception as e:
                print(f"Warning: Failed to parse game card: {e}")
                continue

        return games

    async def _parse_cb_game_card(self, card) -> Optional[NFLGame]:
        """Parse a game card using DraftKings component builder structure."""
        # Get team names
        team_labels = await card.query_selector_all("[class*='cb-market__label-inner--parlay']")
        if len(team_labels) < 2:
            team_labels = await card.query_selector_all("[class*='cb-market__label-inner']")

        if len(team_labels) < 2:
            return None

        away_name = await team_labels[0].inner_text()
        home_name = await team_labels[1].inner_text()

        # Get scores if live
        scores = await card.query_selector_all("[class*='cb-market__scoreboard-team-score']")
        status = "upcoming"
        if len(scores) >= 2:
            status = "live"

        # Get betting buttons (spread, total, moneyline)
        buttons = await card.query_selector_all("[class*='cb-market__button']")

        betting_lines = BettingLines()
        odds_data = []

        for btn in buttons:
            try:
                points_el = await btn.query_selector("[class*='button-points']")
                odds_el = await btn.query_selector("[class*='button-odds']")
                title_el = await btn.query_selector("[class*='button-title']")

                points = await points_el.inner_text() if points_el else ""
                odds = await odds_el.inner_text() if odds_el else ""
                title = await title_el.inner_text() if title_el else ""

                odds_data.append({"points": points, "odds": odds, "title": title})
            except:
                continue

        # Parse odds data - 24 buttons per game card with this layout:
        # Button 0: Away Spread (points + odds)
        # Button 4: Over Total (points + odds, title='O')
        # Button 9: Away Moneyline (just odds)
        # Button 12: Home Spread (points + odds)
        # Button 16: Under Total (points + odds, title='U')
        # Button 21: Home Moneyline (just odds)
        if len(odds_data) >= 22:
            # Spread
            betting_lines.spread = Spread(
                away_line=self._parse_float(odds_data[0]["points"]),
                away_odds=self._parse_american_odds(odds_data[0]["odds"]),
                home_line=self._parse_float(odds_data[12]["points"]),
                home_odds=self._parse_american_odds(odds_data[12]["odds"]),
            )
            # Total
            betting_lines.total = Total(
                over_line=self._parse_float(odds_data[4]["points"]),
                over_odds=self._parse_american_odds(odds_data[4]["odds"]),
                under_line=self._parse_float(odds_data[16]["points"]),
                under_odds=self._parse_american_odds(odds_data[16]["odds"]),
            )
            # Moneyline
            betting_lines.money_line = MoneyLine(
                away=self._parse_american_odds(odds_data[9]["odds"]),
                home=self._parse_american_odds(odds_data[21]["odds"]),
            )

        # Get game time/status
        time_el = await card.query_selector("[class*='cb-market__time'], [class*='event-time']")
        start_time = datetime.now()

        game_id = f"{self._abbreviate(away_name)}_{self._abbreviate(home_name)}_{start_time.strftime('%Y%m%d')}"

        return NFLGame(
            game_id=game_id,
            home_team=Team(name=home_name.strip(), abbreviation=self._abbreviate(home_name)),
            away_team=Team(name=away_name.strip(), abbreviation=self._abbreviate(away_name)),
            start_time=start_time,
            status=status,
            betting_lines=betting_lines,
        )

    def _parse_float(self, text: str) -> Optional[float]:
        """Parse float from text like '+3.5' or 'O 45.5'."""
        if not text:
            return None
        # Remove O/U prefix
        text = text.replace("O", "").replace("U", "").strip()
        try:
            return float(text.replace("+", ""))
        except ValueError:
            return None

    def _parse_american_odds(self, text: str) -> Optional[int]:
        """Parse American odds from text like '−110' or '+150'."""
        if not text:
            return None
        # Handle different minus signs (regular, en-dash, em-dash, minus sign)
        text = text.replace("−", "-").replace("–", "-").replace("—", "-")
        match = re.search(r'([+-]?\d+)', text)
        if match:
            return int(match.group(1))
        return None

    async def _parse_game_card(self, card) -> Optional[NFLGame]:
        """Parse a single game card element."""
        # Get team names
        team_elements = await card.query_selector_all("[class*='event-cell__name']")
        if len(team_elements) < 2:
            team_elements = await card.query_selector_all("[class*='participant']")

        if len(team_elements) < 2:
            return None

        away_name = await team_elements[0].inner_text()
        home_name = await team_elements[1].inner_text()

        # Get betting lines from outcome cells
        outcome_cells = await card.query_selector_all("[class*='sportsbook-outcome-cell']")

        betting_lines = BettingLines()

        # Parse odds (typically: spread, total, moneyline for each team)
        odds_values = []
        for cell in outcome_cells:
            try:
                text = await cell.inner_text()
                odds_values.append(text.strip())
            except:
                odds_values.append("")

        # Parse the odds values
        betting_lines = self._parse_odds_values(odds_values)

        # Get game time
        time_element = await card.query_selector("[class*='event-cell__time']")
        start_time = datetime.now()
        status = "upcoming"

        if time_element:
            time_text = await time_element.inner_text()
            if "LIVE" in time_text.upper():
                status = "live"
            elif "FINAL" in time_text.upper():
                status = "final"

        # Generate game ID from team names
        game_id = f"{self._abbreviate(away_name)}_{self._abbreviate(home_name)}_{start_time.strftime('%Y%m%d')}"

        return NFLGame(
            game_id=game_id,
            home_team=Team(name=home_name.strip(), abbreviation=self._abbreviate(home_name)),
            away_team=Team(name=away_name.strip(), abbreviation=self._abbreviate(away_name)),
            start_time=start_time,
            status=status,
            betting_lines=betting_lines,
        )

    async def _parse_from_table(self, page: Page) -> List[NFLGame]:
        """Fallback parser using table structure."""
        games = []

        # Get all rows from the betting table
        rows = await page.query_selector_all("tbody tr")

        # Process rows in pairs (away, home)
        for i in range(0, len(rows) - 1, 2):
            try:
                away_row = rows[i]
                home_row = rows[i + 1]

                away_name_el = await away_row.query_selector("[class*='event-cell__name'], [class*='participant']")
                home_name_el = await home_row.query_selector("[class*='event-cell__name'], [class*='participant']")

                if not away_name_el or not home_name_el:
                    continue

                away_name = await away_name_el.inner_text()
                home_name = await home_name_el.inner_text()

                # Get odds from both rows
                away_odds = await away_row.query_selector_all("[class*='sportsbook-outcome-cell']")
                home_odds = await home_row.query_selector_all("[class*='sportsbook-outcome-cell']")

                betting_lines = await self._parse_row_odds(away_odds, home_odds)

                game_id = f"{self._abbreviate(away_name)}_{self._abbreviate(home_name)}_{datetime.now().strftime('%Y%m%d')}"

                games.append(NFLGame(
                    game_id=game_id,
                    home_team=Team(name=home_name.strip(), abbreviation=self._abbreviate(home_name)),
                    away_team=Team(name=away_name.strip(), abbreviation=self._abbreviate(away_name)),
                    start_time=datetime.now(),
                    status="upcoming",
                    betting_lines=betting_lines,
                ))
            except Exception as e:
                print(f"Warning: Failed to parse row pair: {e}")
                continue

        return games

    async def _parse_row_odds(self, away_cells, home_cells) -> BettingLines:
        """Parse odds from table row cells."""
        betting_lines = BettingLines()

        # Get text from cells
        away_values = []
        home_values = []

        for cell in away_cells:
            try:
                text = await cell.inner_text()
                away_values.append(text.strip())
            except:
                away_values.append("")

        for cell in home_cells:
            try:
                text = await cell.inner_text()
                home_values.append(text.strip())
            except:
                home_values.append("")

        # Typical column order: Spread, Total, Moneyline
        if len(away_values) >= 3 and len(home_values) >= 3:
            # Parse spread
            betting_lines.spread = self._parse_spread_cell(away_values[0], home_values[0])
            # Parse total
            betting_lines.total = self._parse_total_cell(away_values[1], home_values[1])
            # Parse moneyline
            betting_lines.money_line = self._parse_moneyline_cell(away_values[2], home_values[2])

        return betting_lines

    def _parse_odds_values(self, odds_values: List[str]) -> BettingLines:
        """Parse odds values into BettingLines object."""
        betting_lines = BettingLines()

        # DraftKings typically shows: [away_spread, away_total, away_ml, home_spread, home_total, home_ml]
        if len(odds_values) >= 6:
            # Spread
            away_spread = self._extract_spread(odds_values[0])
            home_spread = self._extract_spread(odds_values[3])
            betting_lines.spread = Spread(
                away_line=away_spread[0],
                away_odds=away_spread[1],
                home_line=home_spread[0],
                home_odds=home_spread[1],
            )

            # Total
            over = self._extract_total(odds_values[1])
            under = self._extract_total(odds_values[4])
            betting_lines.total = Total(
                over_line=over[0],
                over_odds=over[1],
                under_line=under[0],
                under_odds=under[1],
            )

            # Moneyline
            betting_lines.money_line = MoneyLine(
                away=self._extract_odds(odds_values[2]),
                home=self._extract_odds(odds_values[5]),
            )

        return betting_lines

    def _parse_spread_cell(self, away_text: str, home_text: str) -> Spread:
        """Parse spread from cell text."""
        away_spread = self._extract_spread(away_text)
        home_spread = self._extract_spread(home_text)
        return Spread(
            away_line=away_spread[0],
            away_odds=away_spread[1],
            home_line=home_spread[0],
            home_odds=home_spread[1],
        )

    def _parse_total_cell(self, over_text: str, under_text: str) -> Total:
        """Parse total from cell text."""
        over = self._extract_total(over_text)
        under = self._extract_total(under_text)
        return Total(
            over_line=over[0],
            over_odds=over[1],
            under_line=under[0],
            under_odds=under[1],
        )

    def _parse_moneyline_cell(self, away_text: str, home_text: str) -> MoneyLine:
        """Parse moneyline from cell text."""
        return MoneyLine(
            away=self._extract_odds(away_text),
            home=self._extract_odds(home_text),
        )

    def _extract_spread(self, text: str) -> tuple:
        """Extract spread line and odds from text like '+3.5-110' or '-3.5 -110'."""
        if not text:
            return (None, None)

        # Pattern: optional +/- number, then odds
        match = re.search(r'([+-]?\d+\.?\d*)\s*([+-]\d+)?', text)
        if match:
            line = float(match.group(1))
            odds = int(match.group(2)) if match.group(2) else None
            return (line, odds)
        return (None, None)

    def _extract_total(self, text: str) -> tuple:
        """Extract total line and odds from text like 'O 45.5-110' or 'U 45.5 -110'."""
        if not text:
            return (None, None)

        # Pattern: O/U followed by number and odds
        match = re.search(r'[OU]\s*(\d+\.?\d*)\s*([+-]\d+)?', text.upper())
        if match:
            line = float(match.group(1))
            odds = int(match.group(2)) if match.group(2) else None
            return (line, odds)

        # Alternative: just a number with odds
        match = re.search(r'(\d+\.?\d*)\s*([+-]\d+)?', text)
        if match:
            line = float(match.group(1))
            odds = int(match.group(2)) if match.group(2) else None
            return (line, odds)

        return (None, None)

    def _extract_odds(self, text: str) -> Optional[int]:
        """Extract odds from text like '+150' or '-110'."""
        if not text:
            return None

        match = re.search(r'([+-]\d+)', text)
        if match:
            return int(match.group(1))
        return None

    def _abbreviate(self, team_name: str) -> str:
        """Convert team name to abbreviation."""
        team_name = team_name.strip().upper()

        # NFL team abbreviations
        abbreviations = {
            "ARIZONA CARDINALS": "ARI", "CARDINALS": "ARI",
            "ATLANTA FALCONS": "ATL", "FALCONS": "ATL",
            "BALTIMORE RAVENS": "BAL", "RAVENS": "BAL",
            "BUFFALO BILLS": "BUF", "BILLS": "BUF",
            "CAROLINA PANTHERS": "CAR", "PANTHERS": "CAR",
            "CHICAGO BEARS": "CHI", "BEARS": "CHI",
            "CINCINNATI BENGALS": "CIN", "BENGALS": "CIN",
            "CLEVELAND BROWNS": "CLE", "BROWNS": "CLE",
            "DALLAS COWBOYS": "DAL", "COWBOYS": "DAL",
            "DENVER BRONCOS": "DEN", "BRONCOS": "DEN",
            "DETROIT LIONS": "DET", "LIONS": "DET",
            "GREEN BAY PACKERS": "GB", "PACKERS": "GB",
            "HOUSTON TEXANS": "HOU", "TEXANS": "HOU",
            "INDIANAPOLIS COLTS": "IND", "COLTS": "IND",
            "JACKSONVILLE JAGUARS": "JAX", "JAGUARS": "JAX",
            "KANSAS CITY CHIEFS": "KC", "CHIEFS": "KC",
            "LAS VEGAS RAIDERS": "LV", "RAIDERS": "LV",
            "LOS ANGELES CHARGERS": "LAC", "CHARGERS": "LAC",
            "LOS ANGELES RAMS": "LAR", "RAMS": "LAR",
            "MIAMI DOLPHINS": "MIA", "DOLPHINS": "MIA",
            "MINNESOTA VIKINGS": "MIN", "VIKINGS": "MIN",
            "NEW ENGLAND PATRIOTS": "NE", "PATRIOTS": "NE",
            "NEW ORLEANS SAINTS": "NO", "SAINTS": "NO",
            "NEW YORK GIANTS": "NYG", "GIANTS": "NYG",
            "NEW YORK JETS": "NYJ", "JETS": "NYJ",
            "PHILADELPHIA EAGLES": "PHI", "EAGLES": "PHI",
            "PITTSBURGH STEELERS": "PIT", "STEELERS": "PIT",
            "SAN FRANCISCO 49ERS": "SF", "49ERS": "SF",
            "SEATTLE SEAHAWKS": "SEA", "SEAHAWKS": "SEA",
            "TAMPA BAY BUCCANEERS": "TB", "BUCCANEERS": "TB",
            "TENNESSEE TITANS": "TEN", "TITANS": "TEN",
            "WASHINGTON COMMANDERS": "WAS", "COMMANDERS": "WAS",
        }

        for name, abbr in abbreviations.items():
            if name in team_name:
                return abbr

        # Fallback: take first 3 chars
        return team_name[:3] if team_name else "UNK"


async def fetch_nfl_games(headless: bool = True) -> List[NFLGame]:
    """Convenience function to fetch NFL games."""
    async with DraftKingsClient(headless=headless) as client:
        return await client.fetch_nfl_games()
