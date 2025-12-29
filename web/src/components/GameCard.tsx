import type { NFLGame } from '../types/api';
import { LiveBadge } from './LiveBadge';

interface GameCardProps {
  game: NFLGame;
}

export function GameCard({ game }: GameCardProps) {
  const isLive = game.status === 'live';
  const awaySpread = game.betting_lines.spread.away.line;

  return (
    <div
      className={`
        flex-shrink-0 w-64 p-4 rounded-lg
        bg-dk-card border border-dk-border
        hover:border-dk-accent/50 transition-colors
        ${isLive ? 'ring-1 ring-dk-live/30' : ''}
      `}
    >
      {/* Status Badge */}
      <div className="flex justify-between items-center mb-3">
        <span className="text-xs text-gray-500 uppercase">
          {game.status === 'upcoming' ? 'Upcoming' : game.status === 'final' ? 'Final' : ''}
        </span>
        {isLive && <LiveBadge />}
      </div>

      {/* Teams */}
      <div className="space-y-3">
        {/* Away Team */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-dk-bg-light rounded-full flex items-center justify-center text-xs font-bold">
              {game.away_team.abbreviation}
            </div>
            <span className="font-medium text-white">
              {game.away_team.name}
            </span>
          </div>
        </div>

        {/* VS Divider */}
        <div className="flex items-center gap-2">
          <div className="flex-1 h-px bg-dk-border" />
          <span className="text-xs text-gray-500 font-bold">VS</span>
          <div className="flex-1 h-px bg-dk-border" />
        </div>

        {/* Home Team */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-dk-bg-light rounded-full flex items-center justify-center text-xs font-bold">
              {game.home_team.abbreviation}
            </div>
            <span className="font-medium text-white">
              {game.home_team.name}
            </span>
          </div>
        </div>
      </div>

      {/* Quick Odds Preview */}
      <div className="mt-4 pt-3 border-t border-dk-border">
        <div className="flex justify-between text-xs">
          <span className="text-gray-500">Spread</span>
          <span className="text-white font-medium">
            {awaySpread !== null
              ? `${game.away_team.abbreviation} ${awaySpread > 0 ? '+' : ''}${awaySpread}`
              : '-'}
          </span>
        </div>
      </div>
    </div>
  );
}
