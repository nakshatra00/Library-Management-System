<template>
    <div class="container mt-4">
      <h2>User Management</h2>
      <table class="table table-striped">
        <thead>
          <tr>
            <th>Username</th>
            <th>Email</th>
            <th>Role</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.username }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.role }}</td>
            <td>
              <router-link :to="'/admin/users/' + user.id" class="btn btn-primary btn-sm me-2">
                View Details
              </router-link>
              <button @click="confirmDelete(user)" class="btn btn-danger btn-sm">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
  <script>
  export default {
    name: 'UserList',
    data() {
      return {
        users: []
      }
    },
    mounted() {
      this.fetchUsers()
    },
    methods: {
      async fetchUsers() {
        try {
          const response = await this.$axios.get('/api/admin/users')
          this.users = response.data
        } catch (error) {
          console.error('Error fetching users:', error)
          this.$toast.error('Failed to fetch users')
        }
      },
      confirmDelete(user) {
        if (confirm(`Are you sure you want to delete user ${user.username}? This action cannot be undone.`)) {
          this.deleteUser(user.id)
        }
      },
      async deleteUser(userId) {
        try {
          await this.$axios.delete(`/api/admin/users/${userId}`)
          this.$toast.success('User deleted successfully')
          this.fetchUsers()  // Refresh the user list
        } catch (error) {
          console.error('Error deleting user:', error)
          this.$toast.error('Failed to delete user')
        }
      }
    }
  }
  </script>