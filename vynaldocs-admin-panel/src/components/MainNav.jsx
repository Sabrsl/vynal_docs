import React from "react";
import { Link, useLocation } from "react-router-dom";
import { cn } from "../lib/utils";
import { Home, Users, KeyRound, Bell, Settings, Upload } from "lucide-react";

const MainNav = () => {
  const location = useLocation();

  const navItems = [
    {
      title: "Tableau de bord",
      href: "/",
      icon: <Home className="mr-2 h-4 w-4" />
    },
    {
      title: "Utilisateurs",
      href: "/users",
      icon: <Users className="mr-2 h-4 w-4" />
    },
    {
      title: "Licences",
      href: "/licenses",
      icon: <KeyRound className="mr-2 h-4 w-4" />
    },
    {
      title: "Notifications",
      href: "/notifications",
      icon: <Bell className="mr-2 h-4 w-4" />
    },
    {
      title: "Mises à jour",
      href: "/updates",
      icon: <Upload className="mr-2 h-4 w-4" />
    },
    {
      title: "Paramètres",
      href: "/settings",
      icon: <Settings className="mr-2 h-4 w-4" />
    }
  ];

  return (
    <nav className="flex flex-col space-y-1">
      {navItems.map((item) => (
        <Link
          key={item.href}
          to={item.href}
          className={cn(
            "flex items-center px-3 py-2 text-sm font-medium rounded-md hover:bg-accent hover:text-accent-foreground transition-colors",
            location.pathname === item.href 
              ? "bg-accent text-accent-foreground" 
              : "text-muted-foreground"
          )}
        >
          {item.icon}
          {item.title}
        </Link>
      ))}
    </nav>
  );
};

export default MainNav;