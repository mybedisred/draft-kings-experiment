import { useState, useEffect } from 'react';
import { useBetting } from '../context/BettingContext';

function formatOdds(odds: number): string {
  return odds > 0 ? `+${odds}` : String(odds);
}

export function BetSlipModal() {
  const {
    currentBet,
    stake,
    potentialPayout,
    setStake,
    placeBet,
    closeBetSlip,
    isPlacingBet,
    betError,
    bankroll,
  } = useBetting();

  const [stakeInput, setStakeInput] = useState('');

  // Sync stake input with context
  useEffect(() => {
    if (currentBet) {
      setStakeInput(stake > 0 ? String(stake) : '');
    }
  }, [currentBet, stake]);

  if (!currentBet) return null;

  const handleStakeChange = (value: string) => {
    setStakeInput(value);
    const numValue = parseFloat(value);
    if (!isNaN(numValue) && numValue >= 0) {
      setStake(numValue);
    } else if (value === '') {
      setStake(0);
    }
  };

  const handleQuickAmount = (amount: number) => {
    setStakeInput(String(amount));
    setStake(amount);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await placeBet();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/70"
        onClick={closeBetSlip}
      />

      {/* Modal */}
      <div className="relative bg-dk-bg-light border border-dk-border rounded-lg w-full max-w-md mx-4 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-dk-border">
          <h2 className="text-lg font-semibold text-white">Place Bet</h2>
          <button
            onClick={closeBetSlip}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {/* Selection Info */}
          <div className="bg-dk-card rounded-lg p-3 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">
                {currentBet.away_team_abbr} @ {currentBet.home_team_abbr}
              </span>
              <span className={`text-lg font-bold ${currentBet.odds > 0 ? 'text-dk-positive' : 'text-white'}`}>
                {formatOdds(currentBet.odds)}
              </span>
            </div>
            <p className="text-white font-medium">{currentBet.selection}</p>
          </div>

          {/* Stake Input */}
          <div>
            <label className="block text-sm text-gray-400 mb-1">Stake</label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">$</span>
              <input
                type="number"
                step="0.01"
                min="5"
                max="500"
                value={stakeInput}
                onChange={(e) => handleStakeChange(e.target.value)}
                className="w-full bg-dk-bg border border-dk-border rounded-lg px-8 py-2 text-white text-lg
                           focus:outline-none focus:border-dk-accent transition-colors"
                placeholder="0.00"
                autoFocus
              />
            </div>
            <div className="flex gap-2 mt-2">
              {[10, 25, 50, 100].map((amount) => (
                <button
                  key={amount}
                  type="button"
                  onClick={() => handleQuickAmount(amount)}
                  className="flex-1 py-1 px-2 text-sm bg-dk-card hover:bg-dk-card-hover
                             border border-dk-border rounded transition-colors"
                >
                  ${amount}
                </button>
              ))}
            </div>
          </div>

          {/* Payout Info */}
          <div className="bg-dk-card rounded-lg p-3 space-y-1">
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Balance</span>
              <span className="text-white">${bankroll.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-400">Stake</span>
              <span className="text-white">${stake.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-sm border-t border-dk-border pt-1 mt-1">
              <span className="text-gray-400">Potential Payout</span>
              <span className="text-dk-positive font-bold">
                ${potentialPayout.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </span>
            </div>
          </div>

          {/* Error */}
          {betError && (
            <div className="bg-dk-negative/20 border border-dk-negative/50 rounded-lg p-3">
              <p className="text-dk-negative text-sm">{betError}</p>
            </div>
          )}

          {/* Bet Limits */}
          <p className="text-xs text-gray-500 text-center">
            Min $5.00 • Max $500.00
          </p>

          {/* Actions */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={closeBetSlip}
              className="flex-1 py-2 px-4 bg-dk-card hover:bg-dk-card-hover border border-dk-border
                         rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isPlacingBet || stake < 5}
              className="flex-1 py-2 px-4 bg-dk-accent hover:bg-dk-accent/90 text-black font-semibold
                         rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isPlacingBet ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Placing...
                </span>
              ) : (
                'Place Bet'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
