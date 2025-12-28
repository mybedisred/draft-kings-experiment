import type { NFLGame } from '../types/api';
import { GameCard } from './GameCard';

interface FeaturedGamesProps {
  games: NFLGame[];
}

export function FeaturedGames({ games }: FeaturedGamesProps) {
  // Show live games first, then upcoming
  const liveGames = games.filter((g) => g.status === 'live');
  const featuredGames = liveGames.length > 0 ? liveGames : games.slice(0, 4);

  if (featuredGames.length === 0) {
    return null;
  }

  return (
    <section className="mb-8">
      <div className="flex items-center gap-2 mb-4">
        <h2 className="text-lg font-semibold text-white">
          {liveGames.length > 0 ? 'Live Games' : 'Featured Matches'}
        </h2>
        {liveGames.length > 0 && (
          <span className="text-xs bg-dk-live/20 text-dk-live px-2 py-0.5 rounded">
            {liveGames.length} live
          </span>
        )}
      </div>

      <div className="flex gap-4 overflow-x-auto pb-2 -mx-2 px-2">
        {featuredGames.map((game) => (
          <GameCard key={game.game_id} game={game} />
        ))}
      </div>
    </section>
  );
}
