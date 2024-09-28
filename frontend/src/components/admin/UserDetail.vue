<template>
    <div class="container mt-4">
      <h2>User Details</h2>
      <div v-if="user">
        <h3>{{ user.username }}</h3>
        <p><strong>Email:</strong> {{ user.email }}</p>
        <p><strong>Role:</strong> {{ user.role }}</p>
  
        <h4 class="mt-4">Loan History</h4>
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Book</th>
              <th>Date Loaned</th>
              <th>Due Date</th>
              <th>Date Returned</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="loan in loans" :key="loan.id">
              <td>{{ loan.ebook_name }}</td>
              <td>{{ formatDate(loan.date_loaned) }}</td>
              <td>{{ formatDate(loan.due_date) }}</td>
              <td>{{ loan.date_returned ? formatDate(loan.date_returned) : 'N/A' }}</td>
              <td>{{ loan.status }}</td>
            </tr>
          </tbody>
        </table>
  
        <button @click="confirmDelete" class="btn btn-danger mt-4">Delete User</button>
      </div>
      <div v-else>Loading...</div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'UserDetail',
    data() {
      return {
        user: null,
        loans: []
      }
    },
    mounted() {
      this.fetchUserDetails()
    },
    methods: {
      async fetchUserDetails() {
        try {
          const userId = this.$route.params.id
          const response = await this.$axios.get(`/api/admin/users/${userId}`)
          this.user = response.data.user
          this.loans = response.data.loans
        } catch (error) {
          console.error('Error fetching user details:', error)
          this.$toast.error('Failed to fetch user details')
        }
      },
      formatDate(dateString) {
        return new Date(dateString).toLocaleDateString()
      },
      confirmDelete() {
        if (confirm(`Are you sure you want to delete user ${this.user.username}? This action cannot be undone.`)) {
          this.deleteUser()
        }
      },
      async deleteUser() {
        try {
          await this.$axios.delete(`/api/admin/users/${this.user.id}`)
          this.$toast.success('User deleted successfully')
          this.$router.push('/admin/users')  // Redirect to user list
        } catch (error) {
          console.error('Error deleting user:', error)
          this.$toast.error('Failed to delete user')
        }
      }
    }
  }
  </script>