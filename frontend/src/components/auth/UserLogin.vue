<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h2 class="text-center">User Login</h2>
          </div>
          <div class="card-body">
            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label for="username" class="form-label">Username</label>
                <input type="text" class="form-control" id="username" v-model="username" required>
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input type="password" class="form-control" id="password" v-model="password" required>
              </div>
              <div class="d-grid">
                <button type="submit" class="btn btn-primary" :disabled="isLoading">
                  {{ isLoading ? 'Logging in...' : 'Login' }}
                </button>
              </div>
            </form>
            <p v-if="message" class="mt-3 alert" :class="{'alert-success': !isError, 'alert-danger': isError}">{{ message }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';

export default {
  name: 'UserLogin',
  data() {
    return {
      username: '',
      password: '',
      isLoading: false,
      message: '',
      isError: false
    };
  },
  computed: {
    ...mapGetters(['isAuthenticated', 'userRole'])
  },
  methods: {
    ...mapActions(['login']),
    async handleLogin() {
      this.isLoading = true;
      try {
        const user = await this.login({ username: this.username, password: this.password });
        this.message = 'Logged in successfully';
        this.isError = false;
        this.$toast.success(this.message);
        if (user.role === 'admin') {
          this.$router.push('/admindashboard');
        } else {
          this.$router.push('/');
        }
      } catch (error) {
        this.message = error.response?.data?.message || 'Login failed';
        this.isError = true;
        this.$toast.error(this.message);
      } finally {
        this.isLoading = false;
      }
    }
  },
  created() {
    if (this.isAuthenticated) {
      this.$router.push(this.userRole === 'admin' ? '/admindashboard' : '/');
    }
  }
};
</script>