import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3000';

// Configure axios with default settings
axios.defaults.baseURL = API_URL;

// Add a request interceptor to handle token
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('adminToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

// Add a response interceptor to handle token expiration
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('adminToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// User management API calls
export const userAPI = {
  getUsers: (page = 1, limit = 10) => 
    axios.get(`/api/users?page=${page}&limit=${limit}`),
  
  getUserById: (id) => 
    axios.get(`/api/users/${id}`),
  
  createUser: (userData) => 
    axios.post('/api/users', userData),
  
  updateUser: (id, userData) => 
    axios.put(`/api/users/${id}`, userData),
  
  deleteUser: (id) => 
    axios.delete(`/api/users/${id}`),
    
  activateUser: (id) => 
    axios.patch(`/api/users/${id}/activate`),
    
  deactivateUser: (id) => 
    axios.patch(`/api/users/${id}/deactivate`)
};

// License management API calls
export const licenseAPI = {
  getLicenses: (page = 1, limit = 10) => 
    axios.get(`/api/licenses?page=${page}&limit=${limit}`),
  
  getLicenseById: (id) => 
    axios.get(`/api/licenses/${id}`),
  
  createLicense: (licenseData) => 
    axios.post('/api/licenses', licenseData),
  
  updateLicense: (id, licenseData) => 
    axios.put(`/api/licenses/${id}`, licenseData),
  
  deleteLicense: (id) => 
    axios.delete(`/api/licenses/${id}`),
    
  activateLicense: (id) => 
    axios.patch(`/api/licenses/${id}/activate`),
    
  deactivateLicense: (id) => 
    axios.patch(`/api/licenses/${id}/deactivate`)
};

// System settings API calls
export const settingsAPI = {
  getSettings: () => 
    axios.get('/api/settings'),
  
  updateSettings: (settingsData) => 
    axios.put('/api/settings', settingsData)
};

// Statistics API calls
export const statsAPI = {
  getDashboardStats: () => 
    axios.get('/api/stats/dashboard'),
  
  getUserStats: (period = 'month') => 
    axios.get(`/api/stats/users?period=${period}`),
  
  getUsageStats: (period = 'month') => 
    axios.get(`/api/stats/usage?period=${period}`)
};

// Notifications/messages API calls
export const notificationAPI = {
  getNotifications: () => 
    axios.get('/api/notifications'),
  
  sendNotification: (notificationData) => 
    axios.post('/api/notifications', notificationData),
  
  deleteNotification: (id) => 
    axios.delete(`/api/notifications/${id}`)
};

export default {
  userAPI,
  licenseAPI,
  settingsAPI,
  statsAPI,
  notificationAPI
}; 