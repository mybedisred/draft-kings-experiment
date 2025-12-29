import { useState } from 'react';
import { useBetting } from '../context/BettingContext';
import type { BetStatus } from '../types/api';

type FilterTab = 'all' | BetStatus;

function formatOdds(odds: number): string {
  return odds > 0 ? `+${odds}` : String(odds);
}

function getStatusBadge(status: BetStatus) {
  const styles: Record<BetStatus, string> = {
    pending: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    won: 'bg-dk-positive/20 text-dk-positive border-dk-positive/30',
    lost: 'bg-dk-negative/20 text-dk-negative border-dk-negative/30',
    push: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  };

  return (
    <span className={`px-2 py-0.5 text-xs font-medium rounded border ${styles[status]}`}>
      {status.toUpperCase()}
    </span>
  );
}

export function BetHistoryPage() {
  const { bets, bankroll } = useBetting();
  const [activeFilter, setActiveFilter] = useState<FilterTab>('all');

  const filters: { label: string; value: FilterTab }[] = [
    { label: 'All', value: 'all' },
    { label: 'Pending', value: 'pending' },
    { label: 'Won', value: 'won' },
    { label: 'Lost', value: 'lost' },
    { label: 'Push', value: 'push' },
  ];

  const filteredBets = activeFilter === 'all'
    ? bets
    : bets.filter((b) => b.status === activeFilter);

  // Stats
  const stats = {
    totalBets: bets.length,
    pending: bets.filter((b) => b.status === 'pending').length,
    won: bets.filter((b) => b.status === 'won').length,
    lost: bets.filter((b) => b.status === 'lost').length,
    totalWagered: bets.reduce((sum, b) => sum + b.stake, 0),
    totalReturns: bets.reduce((sum, b) => sum + (b.result_amount || 0), 0),
  };

  const profitLoss = stats.totalReturns - stats.totalWagered;

  return (
    <div className="max-w-6xl mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white">Bet History</h1>
        <div className="bg-dk-card px-4 py-2 rounded-lg border border-dk-border">
          <span className="text-sm text-gray-400">Balance: </span>
          <span className="text-lg font-bold text-white">
            ${bankroll.toLocaleString('en-US', { minimumFractionDigits: 2 })}
          </span>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        <div className="bg-dk-card rounded-lg p-4 border border-dk-border">
          <p className="text-xs text-gray-400 uppercase">Total Bets</p>
          <p className="text-2xl font-bold text-white">{stats.totalBets}</p>
        </div>
        <div className="bg-dk-card rounded-lg p-4 border border-dk-border">
          <p className="text-xs text-gray-400 uppercase">Won</p>
          <p className="text-2xl font-bold text-dk-positive">{stats.won}</p>
        </div>
        <div className="bg-dk-card rounded-lg p-4 border border-dk-border">
          <p className="text-xs text-gray-400 uppercase">Lost</p>
          <p className="text-2xl font-bold text-dk-negative">{stats.lost}</p>
        </div>
        <div className="bg-dk-card rounded-lg p-4 border border-dk-border">
          <p className="text-xs text-gray-400 uppercase">Pending</p>
          <p className="text-2xl font-bold text-gray-400">{stats.pending}</p>
        </div>
        <div className="bg-dk-card rounded-lg p-4 border border-dk-border">
          <p className="text-xs text-gray-400 uppercase">Profit/Loss</p>
          <p className={`text-2xl font-bold ${profitLoss >= 0 ? 'text-dk-positive' : 'text-dk-negative'}`}>
            {profitLoss >= 0 ? '+' : ''}${profitLoss.toFixed(2)}
          </p>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 mb-4">
        {filters.map((filter) => (
          <button
            key={filter.value}
            onClick={() => setActiveFilter(filter.value)}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
              activeFilter === filter.value
                ? 'bg-dk-accent text-black'
                : 'bg-dk-card text-gray-400 hover:text-white border border-dk-border'
            }`}
          >
            {filter.label}
          </button>
        ))}
      </div>

      {/* Bets Table */}
      {filteredBets.length === 0 ? (
        <div className="bg-dk-card rounded-lg p-8 text-center border border-dk-border">
          <p className="text-gray-400">No bets found</p>
        </div>
      ) : (
        <div className="bg-dk-card rounded-lg border border-dk-border overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-dk-border bg-dk-bg-light">
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Date</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Game</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Selection</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase">Stake</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase">Odds</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-400 uppercase">Status</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-400 uppercase">Score</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-400 uppercase">Payout</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dk-border">
              {filteredBets.map((bet) => (
                <tr key={bet.id} className="hover:bg-dk-bg/50 transition-colors">
                  <td className="px-4 py-3 text-sm text-gray-400">
                    {new Date(bet.placed_at).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      hour: 'numeric',
                      minute: '2-digit',
                    })}
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-sm font-medium text-white">
                      {bet.away_team_abbr} @ {bet.home_team_abbr}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-sm text-white">{bet.selection}</span>
                  </td>
                  <td className="px-4 py-3 text-right text-sm text-white">
                    ${bet.stake.toFixed(2)}
                  </td>
                  <td className={`px-4 py-3 text-right text-sm font-medium ${
                    bet.odds > 0 ? 'text-dk-positive' : 'text-white'
                  }`}>
                    {formatOdds(bet.odds)}
                  </td>
                  <td className="px-4 py-3 text-center">
                    {getStatusBadge(bet.status)}
                  </td>
                  <td className="px-4 py-3 text-center text-sm text-gray-400">
                    {bet.home_score !== null && bet.away_score !== null ? (
                      `${bet.away_score} - ${bet.home_score}`
                    ) : (
                      '-'
                    )}
                  </td>
                  <td className={`px-4 py-3 text-right text-sm font-medium ${
                    bet.status === 'won' ? 'text-dk-positive' :
                    bet.status === 'lost' ? 'text-dk-negative' :
                    bet.status === 'push' ? 'text-yellow-400' : 'text-gray-400'
                  }`}>
                    {bet.result_amount !== null ? (
                      bet.status === 'won' ? `+$${(bet.result_amount - bet.stake).toFixed(2)}` :
                      bet.status === 'push' ? '$0.00' :
                      `-$${bet.stake.toFixed(2)}`
                    ) : (
                      `$${bet.potential_payout.toFixed(2)}`
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
