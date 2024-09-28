<template>
  <div class="container my-5">
    <h1 class="display-4 text-center mb-5">Welcome to the Library</h1>
    
    <!-- Search Bar -->
      <div class="row justify-content-center mb-5">
        <div class="col-md-8">
          <div class="input-group">
            <input v-model="searchQuery" class="form-control form-control-lg" type="text" placeholder="Search for sections or books...">
            <span class="input-group-text bg-transparent border-0">
              <i class="bi bi-search"></i>
            </span>
          </div>
        </div>
      </div>

    <!-- Sections and Books -->
    <div v-for="section in filteredSections" :key="section.id" class="mb-5">
      <div class="card shadow-sm">
        <div class="card-header bg-light">
          <h2 class="h3 mb-0">{{ section.name }}</h2>
        </div>
        <div class="card-body">
          <p class="lead">{{ section.description }}</p>
          <div class="row row-cols-1 row-cols-md-2 row-cols-lg-4 g-4">
            <div v-for="book in section.books" :key="book.id" class="col">
              <div class="card h-100 shadow-sm">
                <div class="card-body d-flex flex-column">
                  <h5 class="card-title">{{ book.name }}</h5>
                  <p class="card-text">By {{ book.author }}</p>
                  <p class="card-text mt-auto">
                  </p>
                  <router-link :to="{ name: 'BookDetails', params: { id: book.id } }" class="btn btn-outline-primary mt-auto">View Details</router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

export default {
  name: 'HomePage',
  setup() {
    const sections = ref([]);
    const searchQuery = ref('');

    function fetchSections() {
      axios.get('/api/sections')
        .then(function(response) {
          Promise.all(response.data.sections.map(function(section) {
            return axios.get(`/api/sections/${section.id}`)
              .then(function(booksResponse) {
                return {
                  ...section,
                  books: booksResponse.data.books
                };
              });
          }))
          .then(function(sectionsWithBooks) {
            sections.value = sectionsWithBooks;
          });
        })
        .catch(function(error) {
          console.error('Error fetching data:', error);
        });
    }

    onMounted(fetchSections);

    const filteredSections = computed(function() {
      if (!searchQuery.value) return sections.value;
      return sections.value.map(function(section) {
        return {
          ...section,
          books: section.books.filter(function(book) {
            return book.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                   book.author.toLowerCase().includes(searchQuery.value.toLowerCase());
          })
        };
      }).filter(function(section) {
        return section.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
               section.description.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
               section.books.length > 0;
      });
    });

    return {
      sections,
      searchQuery,
      filteredSections
    };
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