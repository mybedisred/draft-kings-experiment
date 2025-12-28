interface OddsButtonProps {
  line?: number | null;
  odds?: number | null;
  label?: string;
  onClick?: () => void;
}

function formatLine(line: number | null | undefined): string {
  if (line === null || line === undefined) return '-';
  return line > 0 ? `+${line}` : String(line);
}

function formatOdds(odds: number | null | undefined): string {
  if (odds === null || odds === undefined) return '-';
  return odds > 0 ? `+${odds}` : String(odds);
}

export function OddsButton({ line, odds, label, onClick }: OddsButtonProps) {
  const hasLine = line !== null && line !== undefined;
  const hasOdds = odds !== null && odds !== undefined;
  const isPositiveOdds = odds !== null && odds !== undefined && odds > 0;

  if (!hasLine && !hasOdds) {
    return (
      <button
        disabled
        className="px-3 py-2 bg-dk-card/50 text-gray-500 rounded text-sm cursor-not-allowed"
      >
        -
      </button>
    );
  }

  return (
    <button
      onClick={onClick}
      className={`
        px-3 py-2 rounded text-sm font-medium
        transition-all duration-200
        hover:scale-105 active:scale-95
        ${isPositiveOdds
          ? 'bg-dk-positive/20 text-dk-positive hover:bg-dk-positive/30 border border-dk-positive/30'
          : 'bg-dk-card hover:bg-dk-card-hover border border-dk-border'
        }
      `}
    >
      <div className="flex flex-col items-center gap-0.5">
        {label && <span className="text-xs text-gray-400">{label}</span>}
        {hasLine && (
          <span className="font-bold">{formatLine(line)}</span>
        )}
        {hasOdds && (
          <span className={`text-xs ${isPositiveOdds ? 'text-dk-positive' : 'text-gray-400'}`}>
            {formatOdds(odds)}
          </span>
        )}
      </div>
    </button>
  );
}
