<template>
  <div class="container mt-5">
    <h2>Books</h2>
    <div v-if="userRole === 'admin'" class="mb-4">
      <router-link to="/add-book" class="btn btn-primary">Add New Book</router-link>
    </div>
    <ul class="list-group">
      <li v-for="book in books" :key="book.id" class="list-group-item d-flex justify-content-between align-items-center">
        <div>
          <h5>
            <router-link :to="{ name: 'BookDetails', params: { id: book.id } }">
              {{ book.name }}
            </router-link>
          </h5>
          <p class="mb-0">Author: {{ book.author }}</p>
          <p class="mb-0">Section: {{ getSectionName(book.section_id) }}</p>
        </div>
        <div v-if="userRole === 'admin'">
          <button @click="editBook(book)" class="btn btn-sm btn-outline-primary me-2">Edit</button>
          <button @click="deleteBook(book.id)" class="btn btn-sm btn-outline-danger">Delete</button>
        </div>
      </li>
    </ul>

    <!-- Edit Modal -->
    <div class="modal fade" id="editBookModal" tabindex="-1" aria-labelledby="editBookModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editBookModalLabel">Edit Book</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateBook">
              <div class="mb-3">
                <label for="bookName" class="form-label">Book Name</label>
                <input v-model="editedBook.name" type="text" class="form-control" id="bookName" required>
              </div>
              <div class="mb-3">
                <label for="bookAuthor" class="form-label">Author</label>
                <input v-model="editedBook.author" type="text" class="form-control" id="bookAuthor" required>
              </div>
              <div class="mb-3">
                <label for="bookContent" class="form-label">Content</label>
                <textarea v-model="editedBook.content" class="form-control" id="bookContent" rows="3" required></textarea>
              </div>
              <div class="mb-3">
                <label for="bookSection" class="form-label">Section</label>
                <select v-model="editedBook.section_id" class="form-select" id="bookSection" required>
                  <option v-for="section in sections" :key="section.id" :value="section.id">
                    {{ section.name }}
                  </option>
                </select>
              </div>
              <button type="submit" class="btn btn-primary">Update Book</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import { Modal } from 'bootstrap';

export default {
  name: 'BookList',
  data() {
    return {
      books: [],
      sections: [],
      editedBook: {
        id: null,
        name: '',
        author: '',
        content: '',
        section_id: null
      },
      editModal: null
    };
  },
  computed: {
    ...mapGetters(['userRole'])
  },
  methods: {
    async fetchBooks() {
      try {
        const response = await this.$axios.get('/api/books');
        this.books = response.data.books;
      } catch (error) {
        console.error('Error fetching books:', error);
        this.$toast.error('Failed to fetch books');
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
    editBook(book) {
      this.editedBook = { ...book };
      this.editModal.show();
    },
    async updateBook() {
      try {
        const response = await this.$axios.put(`/api/books/${this.editedBook.id}`, this.editedBook);
        const updatedBook = response.data.book;
        const index = this.books.findIndex(b => b.id === updatedBook.id);
        if (index !== -1) {
          this.books.splice(index, 1, updatedBook);
        }
        this.editModal.hide();
        this.$toast.success('Book updated successfully');
      } catch (error) {
        console.error('Error updating book:', error);
        this.$toast.error('Failed to update book');
      }
    },
    async deleteBook(bookId) {
      if (confirm('Are you sure you want to delete this book?')) {
        try {
          await this.$axios.delete(`/api/books/${bookId}`);
          this.books = this.books.filter(b => b.id !== bookId);
          this.$toast.success('Book deleted successfully');
        } catch (error) {
          console.error('Error deleting book:', error);
          this.$toast.error('Failed to delete book');
        }
      }
    }
  },
  created() {
    this.fetchBooks();
    this.fetchSections();
  },
  mounted() {
    this.editModal = new Modal(document.getElementById('editBookModal'));
  }
};
</script>