<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h2 class="text-center">User Registration</h2>
          </div>
          <div class="card-body">
            <form @submit.prevent="register">
              <div class="mb-3">
                <label for="username" class="form-label">Username</label>
                <input type="text" class="form-control" id="username" v-model="username" required>
              </div>
              <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input type="email" class="form-control" id="email" v-model="email" required>
              </div>
              <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input type="password" class="form-control" id="password" v-model="password" required>
              </div>
              <div class="d-grid">
                <button type="submit" class="btn btn-primary">Register</button>
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
export default {
  name: 'UserRegister',
  data() {
    return {
      username: '',
      email: '',
      password: '',
      message: '',
      isError: false
    };
  },
  methods: {
    async register() {
      try {
        const response = await this.$axios.post('/register', {
          username: this.username,
          email: this.email,
          password: this.password
        });
        this.message = response.data.message;
        this.isError = false;
        this.$toast.success('Registration successful!');
        
        // Ensure that the router is available and push to the login route
        if (this.$router) {
          this.$router.push({ name: 'UserLogin' });
        }
      } catch (error) {
        this.message = (error.response && error.response.data && error.response.data.message) 
          ? error.response.data.message 
          : 'An error occurred during registration';
        this.isError = true;
        this.$toast.error(this.message);
      }
    }
  }
};
</script>