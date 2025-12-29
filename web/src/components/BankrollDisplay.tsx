import { useBetting } from '../context/BettingContext';

export function BankrollDisplay() {
  const { bankroll } = useBetting();

  return (
    <div className="flex items-center gap-2 bg-dk-card px-3 py-1.5 rounded-lg border border-dk-border">
      <svg className="w-4 h-4 text-dk-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span className="text-sm font-semibold text-white">
        ${bankroll.toLocaleString('en-US', { minimumFractionDigits: 2 })}
      </span>
    </div>
  );
}
