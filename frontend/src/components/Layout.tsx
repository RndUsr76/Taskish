import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ReactNode } from 'react';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const { user, isAdmin, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const isActive = (path: string) =>
    location.pathname === path
      ? 'bg-indigo-700 text-white'
      : 'text-indigo-100 hover:bg-indigo-600';

  return (
    <div className="min-h-screen flex flex-col">
      <nav className="bg-indigo-600 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <Link to="/" className="text-white font-bold text-xl">
                Taskish
              </Link>
              <div className="ml-10 flex items-baseline space-x-4">
                <Link
                  to="/"
                  className={`px-3 py-2 rounded-md text-sm font-medium ${isActive(
                    '/'
                  )}`}
                >
                  Dashboard
                </Link>
                <Link
                  to="/board"
                  className={`px-3 py-2 rounded-md text-sm font-medium ${isActive(
                    '/board'
                  )}`}
                >
                  Team Board
                </Link>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-indigo-100 text-sm">
                {user?.name}{' '}
                <span className="text-indigo-300 text-xs">
                  ({isAdmin ? 'Admin' : 'Member'})
                </span>
              </span>
              <button
                onClick={handleLogout}
                className="bg-indigo-700 hover:bg-indigo-800 text-white px-3 py-2 rounded-md text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>
      <main className="flex-1 max-w-7xl w-full mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}
