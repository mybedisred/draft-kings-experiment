import {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
  type ReactNode,
} from 'react';
import type { Bet, BetType } from '../types/api';
import {
  getBankroll,
  getBets,
  placeBet as placeBetApi,
  calculatePotentialPayout,
} from '../api/betting';

export interface BetSlipItem {
  game_id: string;
  bet_type: BetType;
  selection: string;
  odds: number;
  line_value: number | null;
  home_team_abbr: string;
  away_team_abbr: string;
}

interface BettingContextValue {
  // Bankroll
  bankroll: number;
  refreshBankroll: () => Promise<void>;

  // Bet slip modal
  currentBet: BetSlipItem | null;
  stake: number;
  potentialPayout: number;
  openBetSlip: (bet: BetSlipItem) => void;
  closeBetSlip: () => void;
  setStake: (stake: number) => void;
  placeBet: () => Promise<void>;
  isPlacingBet: boolean;
  betError: string | null;

  // Bet history
  bets: Bet[];
  refreshBets: () => Promise<void>;
  pendingBetsGameIds: Set<string>;
}

const BettingContext = createContext<BettingContextValue | null>(null);

export function BettingProvider({ children }: { children: ReactNode }) {
  // Bankroll state
  const [bankroll, setBankroll] = useState<number>(10000);

  // Bet slip state
  const [currentBet, setCurrentBet] = useState<BetSlipItem | null>(null);
  const [stake, setStakeValue] = useState<number>(0);
  const [isPlacingBet, setIsPlacingBet] = useState(false);
  const [betError, setBetError] = useState<string | null>(null);

  // Bet history state
  const [bets, setBets] = useState<Bet[]>([]);

  // Derived state
  const potentialPayout = currentBet && stake > 0
    ? calculatePotentialPayout(stake, currentBet.odds)
    : 0;

  const pendingBetsGameIds = new Set(
    bets.filter(b => b.status === 'pending').map(b => b.game_id)
  );

  // Fetch bankroll
  const refreshBankroll = useCallback(async () => {
    try {
      const data = await getBankroll();
      setBankroll(data.balance);
    } catch (error) {
      console.error('Failed to fetch bankroll:', error);
    }
  }, []);

  // Fetch bets
  const refreshBets = useCallback(async () => {
    try {
      const data = await getBets({ limit: 100 });
      setBets(data.bets);
    } catch (error) {
      console.error('Failed to fetch bets:', error);
    }
  }, []);

  // Initialize on mount
  useEffect(() => {
    refreshBankroll();
    refreshBets();
  }, [refreshBankroll, refreshBets]);

  // Open bet slip modal
  const openBetSlip = useCallback((bet: BetSlipItem) => {
    setCurrentBet(bet);
    setStakeValue(0);
    setBetError(null);
  }, []);

  // Close bet slip modal
  const closeBetSlip = useCallback(() => {
    setCurrentBet(null);
    setStakeValue(0);
    setBetError(null);
  }, []);

  // Set stake with validation
  const setStake = useCallback((value: number) => {
    setStakeValue(value);
    setBetError(null);
  }, []);

  // Place bet
  const placeBet = useCallback(async () => {
    if (!currentBet || stake <= 0) return;

    // Validate
    if (stake < 5) {
      setBetError('Minimum bet is $5.00');
      return;
    }
    if (stake > 500) {
      setBetError('Maximum bet is $500.00');
      return;
    }
    if (stake > bankroll) {
      setBetError(`Insufficient funds. Balance: $${bankroll.toFixed(2)}`);
      return;
    }

    setIsPlacingBet(true);
    setBetError(null);

    try {
      const response = await placeBetApi({
        game_id: currentBet.game_id,
        bet_type: currentBet.bet_type,
        stake: stake,
        odds: currentBet.odds,
        line_value: currentBet.line_value,
        selection: currentBet.selection,
        home_team_abbr: currentBet.home_team_abbr,
        away_team_abbr: currentBet.away_team_abbr,
      });

      // Update state
      setBankroll(response.bankroll.balance);
      setBets(prev => [response.bet, ...prev]);

      // Close modal
      closeBetSlip();
    } catch (error) {
      setBetError(error instanceof Error ? error.message : 'Failed to place bet');
    } finally {
      setIsPlacingBet(false);
    }
  }, [currentBet, stake, bankroll, closeBetSlip]);

  const value: BettingContextValue = {
    bankroll,
    refreshBankroll,
    currentBet,
    stake,
    potentialPayout,
    openBetSlip,
    closeBetSlip,
    setStake,
    placeBet,
    isPlacingBet,
    betError,
    bets,
    refreshBets,
    pendingBetsGameIds,
  };

  return (
    <BettingContext.Provider value={value}>
      {children}
    </BettingContext.Provider>
  );
}

export function useBetting(): BettingContextValue {
  const context = useContext(BettingContext);
  if (!context) {
    throw new Error('useBetting must be used within a BettingProvider');
  }
  return context;
}
