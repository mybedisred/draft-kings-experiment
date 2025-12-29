import { Link, useLocation } from 'react-router-dom';
import { ConnectionStatus } from './ConnectionStatus';
import { BankrollDisplay } from './BankrollDisplay';

interface HeaderProps {
  isConnected: boolean;
  lastUpdated: Date | null;
  onReconnect: () => void;
}

export function Header({ isConnected, lastUpdated, onReconnect }: HeaderProps) {
  const location = useLocation();

  const navLinks = [
    { to: '/', label: 'Games' },
    { to: '/history', label: 'Bet History' },
  ];

  return (
    <header className="bg-dk-bg-light border-b border-dk-border px-4 py-2">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-6">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3">
            <div className="text-xl font-bold">
              <span className="text-white">NFL</span>
              <span className="text-dk-accent ml-1">Lines</span>
            </div>
            <span className="text-xs text-gray-500 bg-dk-card px-2 py-1 rounded">
              DraftKings
            </span>
          </Link>

          {/* Navigation */}
          <nav className="flex items-center gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`px-3 py-1.5 text-sm font-medium rounded transition-colors ${
                  location.pathname === link.to
                    ? 'bg-dk-accent/20 text-dk-accent'
                    : 'text-gray-400 hover:text-white hover:bg-dk-card'
                }`}
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </div>

        <div className="flex items-center gap-4">
          <BankrollDisplay />
          <ConnectionStatus
            isConnected={isConnected}
            lastUpdated={lastUpdated}
            onReconnect={onReconnect}
          />
        </div>
      </div>
    </header>
  );
}
