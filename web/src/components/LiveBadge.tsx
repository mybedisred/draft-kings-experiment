interface LiveBadgeProps {
  className?: string;
}

export function LiveBadge({ className = '' }: LiveBadgeProps) {
  return (
    <span
      className={`
        inline-flex items-center gap-1 px-1.5 py-0.5
        text-[10px] font-bold uppercase tracking-wider
        bg-dk-live/20 text-dk-live border border-dk-live/50
        rounded animate-pulse-glow
        ${className}
      `}
    >
      <span className="w-1 h-1 bg-dk-live rounded-full" />
      Live
    </span>
  );
}
