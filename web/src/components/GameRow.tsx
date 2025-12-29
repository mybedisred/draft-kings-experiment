import type { NFLGame } from '../types/api';
import { LiveBadge } from './LiveBadge';
import { OddsButton } from './OddsButton';
import { SettleGameButton } from './SettleGameButton';

interface GameRowProps {
  game: NFLGame;
}

export function GameRow({ game }: GameRowProps) {
  const { betting_lines } = game;
  const isLive = game.status === 'live';
  const homeAbbr = game.home_team.abbreviation;
  const awayAbbr = game.away_team.abbreviation;

  // Build selection strings
  const spreadHomeSelection = betting_lines.spread.home.line !== null
    ? `${game.home_team.name} ${betting_lines.spread.home.line > 0 ? '+' : ''}${betting_lines.spread.home.line}`
    : game.home_team.name;
  const spreadAwaySelection = betting_lines.spread.away.line !== null
    ? `${game.away_team.name} ${betting_lines.spread.away.line > 0 ? '+' : ''}${betting_lines.spread.away.line}`
    : game.away_team.name;
  const totalOverSelection = betting_lines.total.over.line !== null
    ? `Over ${betting_lines.total.over.line}`
    : 'Over';
  const totalUnderSelection = betting_lines.total.under.line !== null
    ? `Under ${betting_lines.total.under.line}`
    : 'Under';

  return (
    <tr className="border-b border-dk-border hover:bg-dk-card/50 transition-colors">
      {/* Game Info */}
      <td className="py-3 px-4">
        <div className="space-y-0.5">
          <div className="flex items-center gap-2">
            <span className="w-8 h-8 bg-dk-bg-light rounded flex items-center justify-center text-xs font-bold">
              {awayAbbr}
            </span>
            <span className="text-sm font-medium text-white">{game.away_team.name}</span>
          </div>
          <div className="flex items-center gap-2 pl-1">
            <span className="text-[10px] text-gray-500 w-6 text-center">@</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-8 h-8 bg-dk-bg-light rounded flex items-center justify-center text-xs font-bold">
              {homeAbbr}
            </span>
            <span className="text-sm font-medium text-white">{game.home_team.name}</span>
          </div>
        </div>
      </td>

      {/* Status */}
      <td className="py-3 px-4 text-center">
        {isLive ? (
          <LiveBadge />
        ) : (
          <span className={`text-xs uppercase font-medium ${
            game.status === 'final' ? 'text-gray-500' : 'text-dk-positive'
          }`}>
            {game.status}
          </span>
        )}
      </td>

      {/* Spread */}
      <td className="py-3 px-4">
        <div className="flex flex-col gap-1 items-center">
          <OddsButton
            line={betting_lines.spread.away.line}
            odds={betting_lines.spread.away.odds}
            gameId={game.game_id}
            betType="spread_away"
            selection={spreadAwaySelection}
            homeTeamAbbr={homeAbbr}
            awayTeamAbbr={awayAbbr}
          />
          <OddsButton
            line={betting_lines.spread.home.line}
            odds={betting_lines.spread.home.odds}
            gameId={game.game_id}
            betType="spread_home"
            selection={spreadHomeSelection}
            homeTeamAbbr={homeAbbr}
            awayTeamAbbr={awayAbbr}
          />
        </div>
      </td>

      {/* Total */}
      <td className="py-3 px-4">
        <div className="flex flex-col gap-1 items-center">
          <OddsButton
            label="O"
            line={betting_lines.total.over.line}
            odds={betting_lines.total.over.odds}
            gameId={game.game_id}
            betType="total_over"
            selection={totalOverSelection}
            homeTeamAbbr={homeAbbr}
            awayTeamAbbr={awayAbbr}
          />
          <OddsButton
            label="U"
            line={betting_lines.total.under.line}
            odds={betting_lines.total.under.odds}
            gameId={game.game_id}
            betType="total_under"
            selection={totalUnderSelection}
            homeTeamAbbr={homeAbbr}
            awayTeamAbbr={awayAbbr}
          />
        </div>
      </td>

      {/* Moneyline */}
      <td className="py-3 px-4">
        <div className="flex flex-col gap-1 items-center">
          <OddsButton
            odds={betting_lines.money_line.away}
            gameId={game.game_id}
            betType="ml_away"
            selection={`${game.away_team.name} ML`}
            homeTeamAbbr={homeAbbr}
            awayTeamAbbr={awayAbbr}
          />
          <OddsButton
            odds={betting_lines.money_line.home}
            gameId={game.game_id}
            betType="ml_home"
            selection={`${game.home_team.name} ML`}
            homeTeamAbbr={homeAbbr}
            awayTeamAbbr={awayAbbr}
          />
        </div>
      </td>

      {/* Settle Button */}
      <td className="py-3 px-4">
        <SettleGameButton
          gameId={game.game_id}
          homeTeamAbbr={homeAbbr}
          awayTeamAbbr={awayAbbr}
        />
      </td>
    </tr>
  );
}
