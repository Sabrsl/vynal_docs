import React, { useEffect } from 'react';
import './Notification.css';

const NotificationContainer = ({ notifications, onClose, onMarkAsRead }) => {
  useEffect(() => {
    // Marquer automatiquement comme lu après 5 secondes
    const timeouts = notifications
      .filter(n => !n.read)
      .map(notification => {
        return setTimeout(() => {
          onMarkAsRead(notification.id);
        }, 5000);
      });

    return () => {
      timeouts.forEach(timeout => clearTimeout(timeout));
    };
  }, [notifications, onMarkAsRead]);

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'success':
        return 'bx-check-circle';
      case 'error':
        return 'bx-x-circle';
      case 'warning':
        return 'bx-error';
      case 'info':
        return 'bx-info-circle';
      default:
        return 'bx-bell';
    }
  };

  const getNotificationColor = (type) => {
    switch (type) {
      case 'success':
        return 'var(--color-success)';
      case 'error':
        return 'var(--color-danger)';
      case 'warning':
        return 'var(--color-warning)';
      case 'info':
        return 'var(--color-info)';
      default:
        return 'var(--color-primary)';
    }
  };

  return (
    <div className="notification-container">
      {notifications.map(notification => (
        <div 
          key={notification.id}
          className={`notification ${notification.type} ${notification.read ? 'read' : 'unread'}`}
          style={{ borderLeftColor: getNotificationColor(notification.type) }}
        >
          <div className="notification-icon">
            <i className={`bx ${getNotificationIcon(notification.type)}`}></i>
          </div>
          <div className="notification-content">
            <div className="notification-title">{notification.title}</div>
            <div className="notification-message">{notification.message}</div>
          </div>
          <button 
            className="notification-close"
            onClick={() => onClose(notification.id)}
          >
            <i className='bx bx-x'></i>
          </button>
        </div>
      ))}
    </div>
  );
};

export default NotificationContainer; 