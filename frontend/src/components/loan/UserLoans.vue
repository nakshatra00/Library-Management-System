<template>
  <div class="user-loans container mt-5">
    <h2 class="mb-4">My Loans</h2>
    <div v-if="activeLoans.length > 0" class="row">
      <div v-for="loan in activeLoans" :key="loan.id" class="col-md-6 mb-3">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">{{ loan.book_name }}</h5>
            <p class="card-text">
              <strong>Status:</strong> {{ capitalize(loan.status) }}<br>
              <strong>Loaned on:</strong> {{ formatDate(loan.date_loaned) }}<br>
              <strong>Due on:</strong> {{ formatDate(loan.due_date) }}
            </p>
            <button 
              v-if="loan.status === 'active'"
              @click="handleReturnBook(loan.id)" 
              class="btn btn-primary"
            >
              Return Book
            </button>
          </div>
        </div>
      </div>
    </div>
    <p v-else class="alert alert-info">You have no active loans.</p>

    <h3 class="mt-5 mb-4">Loan History</h3>
    <div v-if="pastLoans.length > 0" class="row">
      <div v-for="loan in pastLoans" :key="loan.id" class="col-md-6 mb-3">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">{{ loan.book_name }}</h5>
            <p class="card-text">
              <strong>Status:</strong> {{ capitalize(loan.status) }}<br>
              <strong>Loaned on:</strong> {{ formatDate(loan.date_loaned) }}<br>
              <strong>Returned on:</strong> {{ formatDate(loan.date_returned) }}
            </p>
          </div>
        </div>
      </div>
    </div>
    <p v-else class="alert alert-info">You have no past loans.</p>
  </div>
</template>

<script>
export default {
  name: 'UserLoans',
  data() {
    return {
      loans: []
    };
  },
  computed: {
    activeLoans() {
      return this.loans.filter(loan => loan.status === 'active');
    },
    pastLoans() {
      return this.loans.filter(loan => loan.status !== 'active');
    }
  },
  methods: {
    async fetchLoans() {
      try {
        const response = await this.$axios.get('/api/user/loans');
        this.loans = response.data.loans;
      } catch (error) {
        console.error('Error fetching loans:', error);
        this.$toast.error('Failed to fetch loans');
      }
    },
    async handleReturnBook(loanId) {
      try {
        await this.$axios.post(`/api/loans/${loanId}/return`);
        this.$toast.success('Book returned successfully');
        this.fetchLoans(); // Refresh the loans list
      } catch (error) {
        console.error('Error returning book:', error);
        this.$toast.error(error.response?.data?.message || 'Failed to return book');
      }
    },
    formatDate(dateString) {
      return dateString ? new Date(dateString).toLocaleString() : 'N/A';
    },
    capitalize(str) {
      return str && typeof str === 'string' ? str.charAt(0).toUpperCase() + str.slice(1) : 'Unknown';
    }
  },
  created() {
    this.fetchLoans();
  }
};
</script>