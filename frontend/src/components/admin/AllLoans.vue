<template>
    <div class="container mt-5">
      <h1 class="mb-4">All Loans</h1>
      <table class="table table-striped">
        <thead>
          <tr>
            <th>User</th>
            <th>Ebook</th>
            <th>Date Loaned</th>
            <th>Due Date</th>
            <th>Date Returned</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="loan in allLoans" :key="loan.id">
            <td>{{ loan.user }}</td>
            <td>{{ loan.ebook }}</td>
            <td>{{ formatDate(loan.date_loaned) }}</td>
            <td>{{ formatDate(loan.due_date) }}</td>
            <td>{{ loan.date_returned ? formatDate(loan.date_returned) : 'Not returned' }}</td>
            <td>
              <span :class="getStatusClass(loan.status)">
                {{ loan.status }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
  <script>
  export default {
    name: 'AllLoans',
    data() {
      return {
        allLoans: []
      }
    },
    mounted() {
      this.fetchAllLoans()
    },
    methods: {
      async fetchAllLoans() {
        try {
          const response = await this.$axios.get('/api/admin/loans/all')
          this.allLoans = response.data
        } catch (error) {
          console.error('Error fetching all loans:', error)
          this.$toast.error('Failed to fetch all loans')
        }
      },
      formatDate(dateString) {
        return new Date(dateString).toLocaleString()
      },
      getStatusClass(status) {
        switch (status) {
          case 'active':
            return 'text-primary'
          case 'returned':
            return 'text-success'
          case 'revoked':
            return 'text-danger'
          default:
            return ''
        }
      }
    }
  }
  </script>