"""Betting logic for payout calculation and bet settlement."""

import random
from typing import Tuple, Optional

from .models import Bet


def calculate_payout(stake: float, odds: int) -> float:
    """
    Calculate potential payout from American odds.

    Returns total payout (stake + profit).
    """
    if odds > 0:
        # Positive odds: profit = stake * (odds / 100)
        profit = stake * (odds / 100)
    else:
        # Negative odds: profit = stake * (100 / abs(odds))
        profit = stake * (100 / abs(odds))

    return round(stake + profit, 2)


def determine_bet_result(
    bet_type: str,
    line_value: Optional[float],
    odds: int,
    stake: float,
    home_score: int,
    away_score: int
) -> Tuple[str, float]:
    """
    Determine if bet won, lost, or pushed based on final scores.

    Returns:
        Tuple of (status, result_amount)
        - 'won': result_amount = full payout (stake + profit)
        - 'lost': result_amount = 0
        - 'push': result_amount = stake (returned)
    """
    score_diff = home_score - away_score  # positive = home wins, negative = away wins
    total_points = home_score + away_score

    if bet_type == 'ml_home':
        # Home team moneyline - home must win outright
        if home_score > away_score:
            return ('won', calculate_payout(stake, odds))
        elif home_score < away_score:
            return ('lost', 0.0)
        else:
            # Tie - push (rare in NFL, but handle it)
            return ('push', stake)

    elif bet_type == 'ml_away':
        # Away team moneyline - away must win outright
        if away_score > home_score:
            return ('won', calculate_payout(stake, odds))
        elif away_score < home_score:
            return ('lost', 0.0)
        else:
            return ('push', stake)

    elif bet_type == 'spread_home':
        # Home team spread - home score + line must beat away score
        # e.g., home -3.5 means home must win by 4+
        # e.g., home +3.5 means home can lose by up to 3
        if line_value is None:
            return ('lost', 0.0)

        adjusted_home = home_score + line_value
        if adjusted_home > away_score:
            return ('won', calculate_payout(stake, odds))
        elif adjusted_home < away_score:
            return ('lost', 0.0)
        else:
            return ('push', stake)

    elif bet_type == 'spread_away':
        # Away team spread - away score + line must beat home score
        if line_value is None:
            return ('lost', 0.0)

        adjusted_away = away_score + line_value
        if adjusted_away > home_score:
            return ('won', calculate_payout(stake, odds))
        elif adjusted_away < home_score:
            return ('lost', 0.0)
        else:
            return ('push', stake)

    elif bet_type == 'total_over':
        # Over bet - total points must exceed the line
        if line_value is None:
            return ('lost', 0.0)

        if total_points > line_value:
            return ('won', calculate_payout(stake, odds))
        elif total_points < line_value:
            return ('lost', 0.0)
        else:
            return ('push', stake)

    elif bet_type == 'total_under':
        # Under bet - total points must be less than the line
        if line_value is None:
            return ('lost', 0.0)

        if total_points < line_value:
            return ('won', calculate_payout(stake, odds))
        elif total_points > line_value:
            return ('lost', 0.0)
        else:
            return ('push', stake)

    # Unknown bet type
    return ('lost', 0.0)


def generate_mock_scores() -> Tuple[int, int]:
    """
    Generate realistic NFL scores for mock settlement.

    NFL scores are typically:
    - Range: 0-50 (usually 10-40)
    - Often divisible by 7 (touchdown) or 3 (field goal)
    - Common scores: 0, 3, 6, 7, 10, 13, 14, 17, 20, 21, 23, 24, 27, 28, 30, 31, 34, 35, 38, 41, 42, 45
    """
    common_scores = [0, 3, 6, 7, 10, 13, 14, 17, 20, 21, 23, 24, 27, 28, 30, 31, 34, 35, 38, 41, 42, 45]

    home_score = random.choice(common_scores)
    away_score = random.choice(common_scores)

    return (home_score, away_score)


def validate_bet_placement(
    stake: float,
    bankroll_balance: float,
    min_bet: float = 5.0,
    max_bet: float = 500.0
) -> Tuple[bool, Optional[str]]:
    """
    Validate a bet can be placed.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if stake < min_bet:
        return (False, f"Minimum bet is ${min_bet:.2f}")

    if stake > max_bet:
        return (False, f"Maximum bet is ${max_bet:.2f}")

    if stake > bankroll_balance:
        return (False, f"Insufficient funds. Balance: ${bankroll_balance:.2f}")

    return (True, None)
