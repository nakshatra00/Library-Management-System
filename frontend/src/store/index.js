import { createStore } from 'vuex';
import axios from 'axios';

export default createStore({
  state: {
    isAuthenticated: false,
    user: null,
    token: null,
    userId: null, 
  },
  getters: {
    isAuthenticated: state => state.isAuthenticated,
    user: state => state.user,
    userId: state => state.userId, 
    userRole: state => state.user ? state.user.role : null,
  },
  mutations: {
    setAuth(state, { user, token }) {
      state.isAuthenticated = true;
      state.user = user;
      state.token = token;
      state.userId = user.id;  
    },
    clearAuth(state) {
      state.isAuthenticated = false;
      state.user = null;
      state.token = null;
      state.userId = null;  
    },
    setUserId(state, userId) {
      state.userId = userId;
    }
  },
  actions: {
    async login({ commit }, credentials) {
      try {
        const response = await axios.post('/login', credentials);
        const { user, access_token } = response.data;
        commit('setAuth', { user, token: access_token });
        sessionStorage.setItem('user', JSON.stringify(user));
        sessionStorage.setItem('token', access_token);
        sessionStorage.setItem('userId', user.id);  // Store userId in sessionStorage
        return user;
      } catch (error) {
        console.error('Login failed:', error);
        throw error;
      }
    },
    async logout({ commit, state }) {
      try {
        const token = state.token;
        if (token) {
          await axios.post('/api/logout', {}, {
            headers: { Authorization: `Bearer ${token}` }
          });
        }
      } catch (error) {
        console.error('Logout failed:', error);
      } finally {
        commit('clearAuth');
        sessionStorage.removeItem('user');
        sessionStorage.removeItem('token');
        sessionStorage.removeItem('userId');  
      }
    },
    checkAuth({ commit }) {
      const user = JSON.parse(sessionStorage.getItem('user'));
      const token = sessionStorage.getItem('token');
      const userId = sessionStorage.getItem('userId');  
      if (user && token) {
        commit('setAuth', { user, token });
        commit('setUserId', userId);
      }
    },
  }
});
