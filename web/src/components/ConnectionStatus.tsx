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
    <div className="flex items-center gap-4 text-sm">
      <div className="flex items-center gap-2">
        <span
          className={`w-2 h-2 rounded-full ${
            isConnected ? 'bg-dk-positive' : 'bg-dk-negative'
          }`}
        />
        <span className="text-gray-400">
          {isConnected ? 'Connected' : 'Disconnected'}
        </span>
      </div>

      {lastUpdated && (
        <span className="text-gray-500">
          Last update: {formatTime(lastUpdated)}
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
