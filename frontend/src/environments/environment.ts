export const environment = {
    production: false,
    apiUrl: '/api/v1',
    wsUrl: `ws://${typeof window !== 'undefined' ? window.location.host : 'localhost:8000'}`
  };
  