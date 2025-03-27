import React, { useEffect } from 'react';
import './Notification.css';

const Notification = ({ 
  id, 
  type = 'info', 
  title, 
  message, 
  duration = 5000, 
  onClose,
  icon
}) => {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose(id);
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [duration, id, onClose]);

  const getIcon = () => {
    if (icon) return icon;
    
    switch (type) {
      case 'success':
        return 'bx-check-circle';
      case 'error':
        return 'bx-x-circle';
      case 'warning':
        return 'bx-error';
      case 'info':
      default:
        return 'bx-info-circle';
    }
  };

  return (
    <div className={`notification notification-${type}`}>
      <div className="notification-icon">
        <i className={`bx ${getIcon()}`}></i>
      </div>
      <div className="notification-content">
        {title && <div className="notification-title">{title}</div>}
        <div className="notification-message">{message}</div>
      </div>
      <button className="notification-close" onClick={() => onClose(id)}>
        <i className='bx bx-x'></i>
      </button>
    </div>
  );
};

export default Notification; 