import { useWebSocket } from './hooks/useWebSocket';
import { Header } from './components/Header';
import { FeaturedGames } from './components/FeaturedGames';
import { GamesTable } from './components/GamesTable';

function App() {
  const { games, isConnected, lastUpdated, error, reconnect } = useWebSocket();

  return (
    <div className="min-h-screen bg-dk-bg text-white">
      <Header
        isConnected={isConnected}
        lastUpdated={lastUpdated}
        onReconnect={reconnect}
      />

      <main className="max-w-7xl mx-auto px-4 py-4">
        {/* Error Banner */}
        {error && (
          <div className="mb-6 p-4 bg-dk-negative/20 border border-dk-negative/50 rounded-lg text-dk-negative">
            <p className="font-medium">Error: {error}</p>
          </div>
        )}

        {/* Loading State */}
        {games.length === 0 && !error && (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="w-12 h-12 border-4 border-dk-accent/30 border-t-dk-accent rounded-full animate-spin mb-4" />
            <p className="text-gray-400">Loading games...</p>
            <p className="text-sm text-gray-500 mt-2">
              {isConnected ? 'Waiting for data from server...' : 'Connecting to server...'}
            </p>
          </div>
        )}

        {/* Content */}
        {games.length > 0 && (
          <>
            <FeaturedGames games={games} />

            <section>
              <h2 className="text-sm font-semibold text-white uppercase tracking-wide mb-2">All Games</h2>
              <GamesTable games={games} />
            </section>

            {/* Footer Info */}
            <div className="mt-4 text-center text-xs text-gray-500">
              <p>
                Showing {games.length} games
                {lastUpdated && ` • Last updated ${lastUpdated.toLocaleTimeString()}`}
              </p>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
