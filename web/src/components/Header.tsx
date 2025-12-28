import { ConnectionStatus } from './ConnectionStatus';

interface HeaderProps {
  isConnected: boolean;
  lastUpdated: Date | null;
  onReconnect: () => void;
}

export function Header({ isConnected, lastUpdated, onReconnect }: HeaderProps) {
  return (
    <header className="bg-dk-bg-light border-b border-dk-border px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="text-2xl font-bold">
            <span className="text-white">NFL</span>
            <span className="text-dk-accent ml-1">Lines</span>
          </div>
          <span className="text-xs text-gray-500 bg-dk-card px-2 py-1 rounded">
            DraftKings
          </span>
        </div>

        <ConnectionStatus
          isConnected={isConnected}
          lastUpdated={lastUpdated}
          onReconnect={onReconnect}
        />
      </div>
    </header>
  );
}
