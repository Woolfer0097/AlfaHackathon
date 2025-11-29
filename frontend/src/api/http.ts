import axios from 'axios';

// Use relative URL in production (via nginx), absolute in dev
const baseURL = import.meta.env.VITE_API_BASE_URL || 
  (import.meta.env.PROD ? '/api/v1' : 'http://localhost:8000/api/v1');

export const httpClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

