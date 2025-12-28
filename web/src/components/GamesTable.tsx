import type { NFLGame } from '../types/api';
import { GameRow } from './GameRow';

interface GamesTableProps {
  games: NFLGame[];
}

export function GamesTable({ games }: GamesTableProps) {
  if (games.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-lg">No games available</p>
        <p className="text-sm mt-2">Waiting for data...</p>
      </div>
    );
  }

  return (
    <div className="bg-dk-card rounded-lg border border-dk-border overflow-hidden">
      <table className="w-full">
        <thead>
          <tr className="bg-dk-bg-light border-b border-dk-border">
            <th className="text-left py-3 px-4 text-sm font-semibold text-gray-400 uppercase tracking-wider">
              Game
            </th>
            <th className="text-center py-3 px-4 text-sm font-semibold text-gray-400 uppercase tracking-wider">
              Status
            </th>
            <th className="text-center py-3 px-4 text-sm font-semibold text-gray-400 uppercase tracking-wider">
              Spread
            </th>
            <th className="text-center py-3 px-4 text-sm font-semibold text-gray-400 uppercase tracking-wider">
              Total
            </th>
            <th className="text-center py-3 px-4 text-sm font-semibold text-gray-400 uppercase tracking-wider">
              Moneyline
            </th>
          </tr>
        </thead>
        <tbody>
          {games.map((game) => (
            <GameRow key={game.game_id} game={game} />
          ))}
        </tbody>
      </table>
    </div>
  );
}
