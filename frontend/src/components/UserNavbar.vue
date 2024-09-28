<!-- UserNavbar.vue -->
<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow">
    <div class="container-fluid">
      <a class="navbar-brand fw-bold" href="#">
        <i class="bi bi-book-half me-2"></i>
        Library Management System
      </a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto">
          <li class="nav-item">
            <router-link class="nav-link" to="/">
              <i class="bi bi-house-door me-1"></i> Dashboard
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/sections">
              <i class="bi bi-grid me-1"></i> Sections
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/my-loans">
              <i class="bi bi-journal-bookmark me-1"></i> My Books
            </router-link>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="#" @click.prevent="handleLogout">
              <i class="bi bi-box-arrow-right me-1"></i> Logout
            </a>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  name: 'UserNavbar',
  methods: {
    ...mapActions(['logout']),
    async handleLogout() {
      await this.logout();
      this.$router.push('/login');
      this.$toast.success('Logged out successfully');
    }
  }
};
</script>

<style scoped>
.navbar {
  padding: 0.5rem 1rem;
}

.nav-link {
  padding: 0.5rem 1rem;
  transition: background-color 0.3s ease;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 0.25rem;
}

.navbar-brand {
  font-size: 1.25rem;
}

@media (max-width: 991.98px) {
  .navbar-nav {
    padding-top: 1rem;
  }
  
  .nav-link {
    padding: 0.75rem 1rem;
  }
}
</style>