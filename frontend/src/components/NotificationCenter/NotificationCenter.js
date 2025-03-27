import React, { useState, useEffect, useRef } from 'react';
import { useNotification } from '../../context/NotificationContext';
import './NotificationCenter.css';

const NotificationCenter = () => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);
  const { notifications, removeNotification, clearAllNotifications } = useNotification();

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

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
    <div className="notification-center" ref={dropdownRef}>
      <button 
        className="notification-toggle"
        onClick={() => setIsOpen(!isOpen)}
      >
        <i className='bx bx-bell'></i>
        {notifications.length > 0 && (
          <span className="notification-badge">{notifications.length}</span>
        )}
      </button>

      {isOpen && (
        <div className="notification-dropdown">
          <div className="notification-header">
            <h3>Notifications</h3>
            {notifications.length > 0 && (
              <button 
                className="clear-all"
                onClick={clearAllNotifications}
              >
                <i className='bx bx-trash'></i>
              </button>
            )}
          </div>

          <div className="notification-list">
            {notifications.length === 0 ? (
              <div className="notification-empty">
                <i className='bx bx-bell-off'></i>
                <p>Aucune notification</p>
              </div>
            ) : (
              notifications.map(notification => (
                <div 
                  key={notification.id}
                  className="notification-item"
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
                    onClick={() => removeNotification(notification.id)}
                  >
                    <i className='bx bx-x'></i>
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationCenter; 