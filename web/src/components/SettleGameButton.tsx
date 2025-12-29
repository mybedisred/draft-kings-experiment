import { useState } from 'react';
import { settleGame } from '../api/betting';
import { useBetting } from '../context/BettingContext';

interface SettleGameButtonProps {
  gameId: string;
  homeTeamAbbr: string;
  awayTeamAbbr: string;
}

export function SettleGameButton({ gameId, homeTeamAbbr, awayTeamAbbr }: SettleGameButtonProps) {
  const { refreshBankroll, refreshBets, pendingBetsGameIds } = useBetting();
  const [isSettling, setIsSettling] = useState(false);
  const [result, setResult] = useState<{ home: number; away: number } | null>(null);

  const hasPendingBets = pendingBetsGameIds.has(gameId);

  if (!hasPendingBets && !result) {
    return null;
  }

  const handleSettle = async () => {
    setIsSettling(true);
    setResult(null);

    try {
      const response = await settleGame(gameId);
      setResult(response.final_score);
      await Promise.all([refreshBankroll(), refreshBets()]);
    } catch (error) {
      console.error('Failed to settle game:', error);
    } finally {
      setIsSettling(false);
    }
  };

  if (result) {
    return (
      <div className="text-center">
        <div className="text-xs text-gray-400 mb-0.5">Final</div>
        <div className="text-sm font-bold text-white">
          {awayTeamAbbr} {result.away} - {result.home} {homeTeamAbbr}
        </div>
      </div>
    );
  }

  return (
    <button
      onClick={handleSettle}
      disabled={isSettling}
      className="px-3 py-1.5 text-xs font-medium bg-dk-accent/20 text-dk-accent
                 hover:bg-dk-accent/30 border border-dk-accent/30 rounded transition-colors
                 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {isSettling ? (
        <span className="flex items-center gap-1">
          <svg className="animate-spin h-3 w-3" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          Settling...
        </span>
      ) : (
        'Simulate End'
      )}
    </button>
  );
}
