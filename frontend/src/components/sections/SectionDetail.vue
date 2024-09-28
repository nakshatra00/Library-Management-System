<!-- SectionDetail.vue -->
<template>
  <div class="container mt-5">
    <h2>{{ section.name }}</h2>
    <p>{{ section.description }}</p>
    <h3>Books in this section</h3>
    <ul class="list-group">
      <li v-for="book in books" :key="book.id" class="list-group-item">
        <h5>{{ book.name }}</h5>
        <p>Author: {{ book.author }}</p>
        <small>Date Issued: {{ new Date(book.date_issued).toLocaleString() }}</small>
        <button class="btn btn-primary mt-2" @click="goToBookDetails(book.id)">View Details</button>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
name: 'SectionDetail',
data: function() {
  return {
    section: {},
    books: []
  };
},
methods: {
  fetchSectionDetails: async function() {
    try {
      const response = await this.$axios.get(`/api/sections/${this.$route.params.id}`);
      this.section = response.data.section;
      this.books = response.data.books;
    } catch (error) {
      this.$toast.error('Failed to fetch section details');
    }
  },
  goToBookDetails: function(bookId) {
    this.$router.push({ name: 'BookDetails', params: { id: bookId } });
  }
},
created: function() {
  this.fetchSectionDetails();
}
};
</script>
