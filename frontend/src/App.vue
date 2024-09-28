<template>
  <div id="app">
    <AdminNavbar v-if="isAuthenticated && userRole === 'admin'" />
    <UserNavbar v-else-if="isAuthenticated" />
    <router-view></router-view>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import AdminNavbar from './components/AdminNavbar.vue';
import UserNavbar from './components/UserNavbar.vue';

export default {
  name: 'App',
  components: {
    AdminNavbar,
    UserNavbar
  },
  computed: {
    ...mapGetters(['isAuthenticated', 'userRole'])
  }
};
</script>