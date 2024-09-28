<template>
  <div class="container-fluid vh-100 d-flex align-items-center justify-content-center bg-light">
    <div class="text-center">
      <h1 class="display-4 mb-4">Welcome to the Library</h1>
      <p class="lead mb-5">Your gateway to knowledge and imagination</p>
      <div class="d-grid gap-2 col-md-6 mx-auto">
        <router-link to="/login" class="btn btn-primary btn-lg">Login</router-link>
        <router-link to="/register" class="btn btn-outline-secondary btn-lg">Register</router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WelcomePage'
}
</script>