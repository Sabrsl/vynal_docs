import React, { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { 
  LayoutDashboard, 
  Users, 
  Key, 
  Settings, 
  Bell, 
  LogOut, 
  Menu, 
  X 
} from 'lucide-react';
import { Button } from './ui/button';

const Layout = () => {
  // Utilisateur fictif pour le développement
  const mockUser = {
    firstName: 'Dev',
    lastName: 'Admin',
    email: 'dev@vynaldocs.com',
    role: 'admin'
  };
  
  const { currentUser, logout } = useAuth();
  // Utiliser mockUser en développement, currentUser en production
  const user = currentUser || mockUser;
  
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleLogout = () => {
    // En développement, juste rediriger vers la page de connexion sans déconnexion réelle
    navigate('/login');
    // En production, utiliser la fonction de déconnexion: logout();
  };

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  // Navigation items
  const navItems = [
    { path: "/", icon: <LayoutDashboard className="mr-2 h-4 w-4" />, label: "Tableau de bord" },
    { path: "/users", icon: <Users className="mr-2 h-4 w-4" />, label: "Utilisateurs" },
    { path: "/licenses", icon: <Key className="mr-2 h-4 w-4" />, label: "Licences" },
    { path: "/settings", icon: <Settings className="mr-2 h-4 w-4" />, label: "Paramètres" },
    { path: "/notifications", icon: <Bell className="mr-2 h-4 w-4" />, label: "Notifications" },
  ];

  return (
    <div className="flex h-screen bg-background">
      {/* Mobile sidebar toggle */}
      <div className="md:hidden fixed z-50 top-4 left-4">
        <Button 
          variant="outline" 
          size="icon" 
          onClick={toggleSidebar}
          aria-label={sidebarOpen ? "Fermer la barre latérale" : "Ouvrir la barre latérale"}
        >
          {sidebarOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
        </Button>
      </div>

      {/* Sidebar */}
      <div 
        className={`${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } md:translate-x-0 fixed md:static z-40 bg-card w-64 h-full transition-transform duration-300 ease-in-out`}
      >
        <div className="flex flex-col h-full">
          <div className="p-4 border-b">
            <h1 className="text-xl font-bold">VynalDocs Admin</h1>
          </div>
          
          <div className="flex-1 overflow-y-auto py-4">
            <nav className="space-y-1 px-2">
              {navItems.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) => 
                    `flex items-center px-2 py-2 text-sm font-medium rounded-md ${
                      isActive 
                        ? 'bg-primary text-primary-foreground' 
                        : 'text-foreground hover:bg-accent hover:text-accent-foreground'
                    }`
                  }
                  end={item.path === '/'}
                >
                  {item.icon}
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </div>
          
          <div className="p-4 border-t">
            <div className="flex items-center mb-4">
              <div className="h-8 w-8 rounded-full bg-primary flex items-center justify-center text-primary-foreground">
                {user?.firstName?.[0] || user?.email?.[0] || 'A'}
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium">{user?.firstName} {user?.lastName}</p>
                <p className="text-xs text-muted-foreground">{user?.email}</p>
              </div>
            </div>
            <Button 
              variant="outline" 
              className="w-full justify-start"
              onClick={handleLogout}
            >
              <LogOut className="mr-2 h-4 w-4" />
              Déconnexion
            </Button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout; 