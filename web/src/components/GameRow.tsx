import type { NFLGame } from '../types/api';
import { LiveBadge } from './LiveBadge';
import { OddsButton } from './OddsButton';

interface GameRowProps {
  game: NFLGame;
}

export function GameRow({ game }: GameRowProps) {
  const { betting_lines } = game;
  const isLive = game.status === 'live';

  return (
    <tr className="border-b border-dk-border hover:bg-dk-card/50 transition-colors">
      {/* Game Info */}
      <td className="py-2 px-3">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <span className="w-6 h-6 bg-dk-bg-light rounded flex items-center justify-center text-[10px] font-bold">
              {game.away_team.abbreviation}
            </span>
            <span className="text-sm text-white">{game.away_team.name}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-6 h-6 bg-dk-bg-light rounded flex items-center justify-center text-[10px] font-bold">
              {game.home_team.abbreviation}
            </span>
            <span className="text-sm text-white">{game.home_team.name}</span>
          </div>
        </div>
      </td>

      {/* Status */}
      <td className="py-2 px-3 text-center">
        {isLive ? (
          <LiveBadge />
        ) : (
          <span className={`text-[10px] uppercase font-medium ${
            game.status === 'final' ? 'text-gray-500' : 'text-dk-positive'
          }`}>
            {game.status}
          </span>
        )}
      </td>

      {/* Spread */}
      <td className="py-2 px-3">
        <div className="flex flex-col gap-0.5 items-center">
          <OddsButton
            line={betting_lines.spread.away.line}
            odds={betting_lines.spread.away.odds}
          />
          <OddsButton
            line={betting_lines.spread.home.line}
            odds={betting_lines.spread.home.odds}
          />
        </div>
      </td>

      {/* Total */}
      <td className="py-2 px-3">
        <div className="flex flex-col gap-0.5 items-center">
          <OddsButton
            label="O"
            line={betting_lines.total.over.line}
            odds={betting_lines.total.over.odds}
          />
          <OddsButton
            label="U"
            line={betting_lines.total.under.line}
            odds={betting_lines.total.under.odds}
          />
        </div>
      </td>

      {/* Moneyline */}
      <td className="py-2 px-3">
        <div className="flex flex-col gap-0.5 items-center">
          <OddsButton odds={betting_lines.money_line.away} />
          <OddsButton odds={betting_lines.money_line.home} />
        </div>
      </td>
    </tr>
  );
}
