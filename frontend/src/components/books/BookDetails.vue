<template>
  <div class="container mt-5" v-if="book">
    <div class="card shadow-sm">
      <div class="card-body">
        <h2 class="card-title mb-4">{{ book.name }}</h2>
        <div class="row">
          <div class="col-md-6">
            <p><i class="bi bi-person me-2"></i><strong>Author:</strong> {{ book.author }}</p>
            <p><i class="bi bi-bookmark me-2"></i><strong>Section:</strong> {{ getSectionName(book.section_id) }}</p>
            <p><i class="bi bi-calendar me-2"></i><strong>Date Issued:</strong> {{ formatDate(book.date_issued) }}</p>
          </div>
          <div class="col-md-6">
            <p><strong>Description:</strong></p>
            <p class="text-muted">{{ book.content }}</p>
          </div>
        </div>
        
        <div class="mt-4">
          <h3 class="mb-3">Loan Status</h3>
          <p class="alert" :class="getLoanStatusClass()">
            {{ getLoanStatus() }}
          </p>
        </div>
        
        <div class="mt-4">
          <button 
            v-if="userRole !== 'admin' && isBookAvailable()" 
            @click="handleLoanBook" 
            class="btn btn-primary"
          >
            <i class="bi bi-book me-2"></i>Loan Book
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'BookDetails',
  data() {
    return {
      book: null,
      sections: []
    };
  },
  computed: {
    ...mapGetters(['userRole'])
  },
  methods: {
    async fetchBookDetails() {
      try {
        const response = await this.$axios.get(`/api/books/${this.$route.params.id}`);
        this.book = response.data.book;
        if (!this.book.loan_info) {
          this.book.loan_info = { status: 'available' };
        }
      } catch (error) {
        console.error('Error fetching book details:', error);
        this.$toast.error('Failed to fetch book details');
      }
    },
    async fetchSections() {
      try {
        const response = await this.$axios.get('/api/sections');
        this.sections = response.data.sections;
      } catch (error) {
        console.error('Error fetching sections:', error);
        this.$toast.error('Failed to fetch sections');
      }
    },
    getSectionName(sectionId) {
      const section = this.sections.find(s => s.id === sectionId);
      return section ? section.name : 'Unknown';
    },
    async handleLoanBook() {
      try {
        await this.$axios.post('/api/loans', { book_id: this.book.id });
        this.$toast.success('Book loaned successfully');
        this.fetchBookDetails();  // Refresh book details after loaning
      } catch (error) {
        this.$toast.error(error.response?.data?.message || 'Failed to loan book');
      }
    },
    formatDate(dateString) {
      return dateString ? new Date(dateString).toLocaleString() : 'N/A';
    },
    getLoanStatus() {
      if (!this.book || !this.book.loan_info || !this.book.loan_info.status) {
        return 'Unknown';
      }
      return this.capitalize(this.book.loan_info.status);
    },
    getLoanStatusClass() {
      const status = this.getLoanStatus().toLowerCase();
      switch(status) {
        case 'available':
          return 'alert-success';
        case 'active':
          return 'alert-warning';
        case 'returned':
        case 'revoked':
          return 'alert-info';
        default:
          return 'alert-secondary';
      }
    },
    isBookAvailable() {
      return this.getLoanStatus().toLowerCase() === 'available';
    },
    capitalize(str) {
      return str && typeof str === 'string' ? str.charAt(0).toUpperCase() + str.slice(1) : 'Unknown';
    }
  },
  created() {
    this.fetchBookDetails();
    this.fetchSections();
  }
};
</script>

<style scoped>
.card {
  transition: transform 0.2s;
}
.card:hover {
  transform: translateY(-5px);
}
</style>