interface ConnectionStatusProps {
  isConnected: boolean;
  lastUpdated: Date | null;
  onReconnect: () => void;
}

export function ConnectionStatus({ isConnected, lastUpdated, onReconnect }: ConnectionStatusProps) {
  const formatTime = (date: Date | null) => {
    if (!date) return 'Never';
    return date.toLocaleTimeString();
  };

  return (
    <div className="flex items-center gap-3 text-xs">
      <div className="flex items-center gap-1.5">
        <span
          className={`w-1.5 h-1.5 rounded-full ${
            isConnected ? 'bg-dk-positive' : 'bg-dk-negative'
          }`}
        />
        <span className="text-gray-400">
          {isConnected ? 'Live' : 'Offline'}
        </span>
      </div>

      {lastUpdated && (
        <span className="text-gray-500 hidden sm:inline">
          {formatTime(lastUpdated)}
        </span>
      )}

      {!isConnected && (
        <button
          onClick={onReconnect}
          className="px-2 py-1 text-xs bg-dk-accent/20 text-dk-accent rounded hover:bg-dk-accent/30 transition-colors"
        >
          Reconnect
        </button>
      )}
    </div>
  );
}
