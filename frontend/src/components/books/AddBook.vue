<!-- AddBook.vue -->
<template>
  <div class="container mt-5">
    <h2>Add New Book</h2>
    <form @submit.prevent="addBook">
      <div class="mb-3">
        <label for="bookName" class="form-label">Book Name</label>
        <input type="text" class="form-control" id="bookName" v-model="newBook.name" required>
      </div>
      <div class="mb-3">
        <label for="bookAuthor" class="form-label">Author</label>
        <input type="text" class="form-control" id="bookAuthor" v-model="newBook.author" required>
      </div>
      <div class="mb-3">
        <label for="bookContent" class="form-label">Content</label>
        <textarea class="form-control" id="bookContent" v-model="newBook.content" required></textarea>
      </div>
      <div class="mb-3">
        <label for="bookSection" class="form-label">Section</label>
        <select class="form-control" id="bookSection" v-model="newBook.section_id" required>
          <option v-for="section in sections" :key="section.id" :value="section.id">
            {{ section.name }}
          </option>
        </select>
      </div>
      <button type="submit" class="btn btn-primary">Add Book</button>
    </form>
  </div>
</template>

<script>
export default {
  name: 'AddBook',
  data() {
    return {
      newBook: {
        name: '',
        author: '',
        content: '',
        section_id: null
      },
      sections: []
    };
  },
  methods: {
    async addBook() {
      try {
        await this.$axios.post('/api/books', this.newBook);
        this.$toast.success('Book added successfully');
        this.$router.push('/books');
      } catch (error) {
        this.$toast.error(error.response?.data?.message || 'Failed to add book');
      }
    },
    async fetchSections() {
      try {
        const response = await this.$axios.get('/api/sections');
        this.sections = response.data.sections;
      } catch (error) {
        this.$toast.error('Failed to fetch sections');
      }
    }
  },
  created() {
    this.fetchSections();
  }
};
</script>
