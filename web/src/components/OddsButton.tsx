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
        className="min-w-[70px] px-2 py-1 bg-dk-card/50 text-gray-500 rounded text-xs cursor-not-allowed"
      >
        -
      </button>
    );
  }

  return (
    <button
      onClick={onClick}
      className={`
        min-w-[70px] px-2 py-1 rounded text-xs font-medium
        transition-all duration-150
        hover:scale-102 active:scale-98
        ${isPositiveOdds
          ? 'bg-dk-positive/20 text-dk-positive hover:bg-dk-positive/30 border border-dk-positive/30'
          : 'bg-dk-card hover:bg-dk-card-hover border border-dk-border'
        }
      `}
    >
      <div className="flex items-center justify-center gap-1">
        {label && <span className="text-[10px] text-gray-400">{label}</span>}
        {hasLine && (
          <span className="font-bold text-xs">{formatLine(line)}</span>
        )}
        {hasOdds && (
          <span className={`text-[10px] ${isPositiveOdds ? 'text-dk-positive' : 'text-gray-400'}`}>
            ({formatOdds(odds)})
          </span>
        )}
      </div>
    </button>
  );
}
