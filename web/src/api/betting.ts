import type {
  Bankroll,
  Bet,
  BetStatus,
  BetsResponse,
  PlaceBetRequest,
  PlaceBetResponse,
  SettleGameResponse,
} from '../types/api';

const API_BASE = '/api';

export async function getBankroll(): Promise<Bankroll> {
  const response = await fetch(`${API_BASE}/bankroll`);
  if (!response.ok) {
    throw new Error('Failed to fetch bankroll');
  }
  return response.json();
}

export async function placeBet(request: PlaceBetRequest): Promise<PlaceBetResponse> {
  const response = await fetch(`${API_BASE}/bets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to place bet');
  }

  return response.json();
}

export async function getBets(params?: {
  status?: BetStatus;
  limit?: number;
  offset?: number;
}): Promise<BetsResponse> {
  const searchParams = new URLSearchParams();

  if (params?.status) {
    searchParams.set('status', params.status);
  }
  if (params?.limit) {
    searchParams.set('limit', String(params.limit));
  }
  if (params?.offset) {
    searchParams.set('offset', String(params.offset));
  }

  const url = `${API_BASE}/bets${searchParams.toString() ? `?${searchParams}` : ''}`;
  const response = await fetch(url);

  if (!response.ok) {
    throw new Error('Failed to fetch bets');
  }

  return response.json();
}

export async function getBet(betId: number): Promise<{ bet: Bet }> {
  const response = await fetch(`${API_BASE}/bets/${betId}`);

  if (!response.ok) {
    throw new Error('Failed to fetch bet');
  }

  return response.json();
}

export async function settleGame(gameId: string): Promise<SettleGameResponse> {
  const response = await fetch(`${API_BASE}/games/${gameId}/settle`, {
    method: 'POST',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to settle game');
  }

  return response.json();
}

export function calculatePotentialPayout(stake: number, odds: number): number {
  if (odds > 0) {
    return Math.round((stake + (stake * odds) / 100) * 100) / 100;
  } else {
    return Math.round((stake + (stake * 100) / Math.abs(odds)) * 100) / 100;
  }
}
