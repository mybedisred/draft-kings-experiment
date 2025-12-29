export interface Team {
  name: string;
  abbreviation: string;
}

export interface MoneyLine {
  home: number | null;
  away: number | null;
}

export interface SpreadLine {
  line: number | null;
  odds: number | null;
}

export interface Spread {
  home: SpreadLine;
  away: SpreadLine;
}

export interface TotalLine {
  line: number | null;
  odds: number | null;
}

export interface Total {
  over: TotalLine;
  under: TotalLine;
}

export interface BettingLines {
  money_line: MoneyLine;
  spread: Spread;
  total: Total;
}

export interface NFLGame {
  game_id: string;
  home_team: Team;
  away_team: Team;
  start_time: string;
  status: 'upcoming' | 'live' | 'final';
  betting_lines: BettingLines;
  fetched_at: string;
}

export interface GamesResponse {
  games: NFLGame[];
  last_updated: string | null;
  count: number;
}

export interface HealthResponse {
  status: string;
  last_updated: string | null;
  is_fetching: boolean;
  game_count: number;
  websocket_clients: number;
  fetch_count: number;
  last_error: string | null;
}

export interface WebSocketMessage {
  type: 'connection_established' | 'games_update' | 'error' | 'pong';
  timestamp: string;
  game_count?: number;
  games?: NFLGame[];
  last_updated?: string | null;
  error?: string;
}

// ==================== BETTING TYPES ====================

export type BetType = 'spread_home' | 'spread_away' | 'total_over' | 'total_under' | 'ml_home' | 'ml_away';
export type BetStatus = 'pending' | 'won' | 'lost' | 'push';

export interface Bet {
  id: number;
  game_id: string;
  bet_type: BetType;
  selection: string;
  stake: number;
  odds: number;
  potential_payout: number;
  status: BetStatus;
  result_amount: number | null;
  home_score: number | null;
  away_score: number | null;
  placed_at: string;
  settled_at: string | null;
  home_team_abbr: string;
  away_team_abbr: string;
  line_value: number | null;
}

export interface Bankroll {
  balance: number;
  updated_at: string;
}

export interface PlaceBetRequest {
  game_id: string;
  bet_type: BetType;
  stake: number;
  odds: number;
  line_value: number | null;
  selection: string;
  home_team_abbr: string;
  away_team_abbr: string;
}

export interface PlaceBetResponse {
  bet: Bet;
  bankroll: Bankroll;
}

export interface BetsResponse {
  bets: Bet[];
  total_count: number;
  limit: number;
  offset: number;
}

export interface SettleGameResponse {
  game_id: string;
  final_score: { home: number; away: number };
  settled_bets: Bet[];
  bankroll: Bankroll;
}
