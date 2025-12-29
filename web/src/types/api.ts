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
