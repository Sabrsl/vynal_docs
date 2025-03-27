import React, { createContext, useContext, useState, useCallback } from 'react';

const NotificationContext = createContext();

export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const addNotification = useCallback(({ 
    type = 'info', 
    title,
    message,
    duration = 5000,
    icon
  }) => {
    const id = Date.now();
    const newNotification = {
      id,
      type,
      title,
      message,
      duration,
      icon,
      read: false,
      timestamp: new Date().toISOString()
    };
    
    setNotifications(prev => [newNotification, ...prev]);
    setUnreadCount(prev => prev + 1);

    if (duration !== 0) {
      setTimeout(() => {
        removeNotification(id);
      }, duration);
    }

    return id;
  }, []);

  const removeNotification = useCallback((id) => {
    setNotifications(prev => {
      const notification = prev.find(n => n.id === id);
      if (notification && !notification.read) {
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
      return prev.filter(n => n.id !== id);
    });
  }, []);

  const markAsRead = useCallback((id) => {
    setNotifications(prev => {
      return prev.map(notification => {
        if (notification.id === id && !notification.read) {
          setUnreadCount(prev => Math.max(0, prev - 1));
          return { ...notification, read: true };
        }
        return notification;
      });
    });
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications(prev => {
      return prev.map(notification => ({ ...notification, read: true }));
    });
    setUnreadCount(0);
  }, []);

  const clearAllNotifications = useCallback(() => {
    setNotifications([]);
    setUnreadCount(0);
  }, []);

  const success = useCallback((title, message, duration) => {
    return addNotification({ type: 'success', title, message, duration });
  }, [addNotification]);

  const error = useCallback((title, message, duration) => {
    return addNotification({ type: 'error', title, message, duration });
  }, [addNotification]);

  const warning = useCallback((title, message, duration) => {
    return addNotification({ type: 'warning', title, message, duration });
  }, [addNotification]);

  const info = useCallback((title, message, duration) => {
    return addNotification({ type: 'info', title, message, duration });
  }, [addNotification]);

  const value = {
    notifications,
    unreadCount,
    addNotification,
    removeNotification,
    markAsRead,
    markAllAsRead,
    success,
    error,
    warning,
    info,
    clearAllNotifications
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
}; 