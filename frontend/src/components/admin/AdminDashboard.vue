<template>
  <div class="container mt-5">
    <h1 class="mb-4 text-center">Admin Dashboard</h1>
    <div class="row row-cols-1 row-cols-md-3 g-4">
      <div class="col" v-for="(card, index) in cards" :key="index">
        <div class="card h-100 shadow-sm" @click="navigateTo(card.route)">
          <div class="card-body d-flex flex-column justify-content-center align-items-center">
            <i :class="['bi', card.icon, 'display-4 mb-3 text-primary']"></i>
            <h5 class="card-title text-center">{{ card.title }}</h5>
            <p class="card-text text-center text-muted">{{ card.description }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminDashboard',
  data() {
    return {
      cards: [
        { title: 'Add Section', description: 'Create a new section', route: '/add-section', icon: 'bi-folder-plus' },
        { title: 'Add Book', description: 'Add a new book', route: '/add-book', icon: 'bi-book' },
        { title: 'Active Loans', description: 'View active loans', route: '/active-loans', icon: 'bi-bookmark-check' },
        { title: 'All Loans', description: 'View all loans', route: '/all-loans', icon: 'bi-bookmarks' },
        { title: 'All Sections', description: 'View all sections', route: '/sections', icon: 'bi-folder' },
        { title: 'All Books', description: 'View all books', route: '/books', icon: 'bi-book-half' },
      ],
    };
  },
  methods: {
    navigateTo(route) {
      this.$router.push(route);
    },
  },
};
</script>

<style scoped>
.card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
}
</style>