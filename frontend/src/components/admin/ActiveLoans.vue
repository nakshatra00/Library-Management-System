<template>
    <div class="container mt-5">
      <h1 class="mb-4">Active Loans</h1>
      <table class="table table-striped">
        <thead>
          <tr>
            <th>User</th>
            <th>Ebook</th>
            <th>Date Loaned</th>
            <th>Due Date</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="loan in activeLoans" :key="loan.id">
            <td>{{ loan.user }}</td>
            <td>{{ loan.ebook }}</td>
            <td>{{ formatDate(loan.date_loaned) }}</td>
            <td>{{ formatDate(loan.due_date) }}</td>
            <td>
              <button @click="revokeLoan(loan.id)" class="btn btn-warning btn-sm">Revoke</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
  <script>
  export default {
    name: 'ActiveLoans',
    data() {
      return {
        activeLoans: []
      }
    },
    mounted() {
      this.fetchActiveLoans()
    },
    methods: {
      async fetchActiveLoans() {
        try {
          const response = await this.$axios.get('/api/admin/loans/active')
          this.activeLoans = response.data
        } catch (error) {
          console.error('Error fetching active loans:', error)
          this.$toast.error('Failed to fetch active loans')
        }
      },
      async revokeLoan(loanId) {
        try {
          await this.$axios.post(`/api/admin/loans/revoke/${loanId}`)
          this.$toast.success('Loan revoked successfully')
          this.fetchActiveLoans()
        } catch (error) {
          console.error('Error revoking loan:', error)
          this.$toast.error('Failed to revoke loan')
        }
      },
      formatDate(dateString) {
        return new Date(dateString).toLocaleString()
      }
    }
  }
  </script>