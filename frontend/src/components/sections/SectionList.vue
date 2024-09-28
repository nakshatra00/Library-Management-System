<template>
  <div class="container mt-5">
    <h2>Sections</h2>
    <div v-if="userRole === 'admin'" class="mb-4">
      <form @submit.prevent="addSection" class="row g-3 align-items-end">
        <div class="col">
          <input type="text" class="form-control" placeholder="Section Name" v-model="newSection.name" required>
        </div>
        <div class="col">
          <input type="text" class="form-control" placeholder="Description" v-model="newSection.description" required>
        </div>
        <div class="col-auto">
          <button type="submit" class="btn btn-primary" :disabled="!isValidSection">Add Section</button>
        </div>
      </form>
    </div>
    <div class="mt-4">
      <h3>Existing Sections</h3>
      <ul class="list-group">
        <li v-for="section in sections" :key="section.id" class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <router-link :to="'/section/' + section.id">
                <h5>{{ section.name }}</h5>
              </router-link>
              <p>{{ section.description }}</p>
              </div>
            <div v-if="userRole === 'admin'">
              <button @click="editSection(section)" class="btn btn-sm btn-outline-primary me-2">Edit</button>
              <button @click="confirmDelete(section)" class="btn btn-sm btn-outline-danger">Delete</button>
            </div>
          </div>
        </li>
      </ul>
    </div>

    <!-- Edit Section Modal -->
    <div v-if="showEditModal" class="modal fade show" tabindex="-1" style="display: block;">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit Section</h5>
            <button type="button" class="btn-close" @click="closeEditModal"></button>
          </div>
          <div class="modal-body">
            <form>
              <div class="mb-3">
                <label for="editSectionName" class="form-label">Section Name</label>
                <input type="text" class="form-control" id="editSectionName" v-model="editingSection.name" required>
              </div>
              <div class="mb-3">
                <label for="editSectionDescription" class="form-label">Description</label>
                <textarea class="form-control" id="editSectionDescription" v-model="editingSection.description" required></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeEditModal">Close</button>
            <button type="button" class="btn btn-primary" @click="updateSection">Save changes</button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showEditModal" class="modal-backdrop fade show"></div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

export default {
  name: 'SectionList',
  data() {
    return {
      newSection: {
        name: '',
        description: ''
      },
      sections: [],
      editingSection: null,
      showEditModal: false
    };
  },
  computed: {
    ...mapGetters(['userRole']),
    isValidSection() {
      return this.newSection.name.trim() !== '' && this.newSection.description.trim() !== '';
    }
  },
  methods: {
    async addSection() {
      if (!this.isValidSection) return;
      try {
        const response = await this.$axios.post('/api/sections', this.newSection);
        this.$toast.success('Section added successfully');
        this.sections.push(response.data.section);
        this.newSection.name = '';
        this.newSection.description = '';
      } catch (error) {
        this.$toast.error(error.response?.data?.message || 'Failed to add section');
      }
    },
    async fetchSections() {
      try {
        const response = await this.$axios.get('/api/sections');
        this.sections = response.data.sections;
      } catch (error) {
        this.$toast.error('Failed to fetch sections');
      }
    },
    editSection(section) {
      this.editingSection = { ...section };
      this.showEditModal = true;
    },
    closeEditModal() {
      this.showEditModal = false;
      this.editingSection = null;
    },
    async updateSection() {
      try {
        const response = await this.$axios.put(`/api/sections/${this.editingSection.id}`, {
          name: this.editingSection.name,
          description: this.editingSection.description
        });
        const index = this.sections.findIndex(s => s.id === this.editingSection.id);
        this.sections[index] = response.data.section;
        this.$toast.success('Section updated successfully');
        this.closeEditModal();
      } catch (error) {
        this.$toast.error(error.response?.data?.message || 'Failed to update section');
      }
    },
    confirmDelete(section) {
      if (confirm(`Are you sure you want to delete "${section.name}"? This will also delete all books in this section.`)) {
        this.deleteSection(section);
      }
    },
    async deleteSection(section) {
      try {
        await this.$axios.delete(`/api/sections/${section.id}`);
        this.sections = this.sections.filter(s => s.id !== section.id);
        this.$toast.success('Section and associated books deleted successfully');
      } catch (error) {
        this.$toast.error(error.response?.data?.message || 'Failed to delete section');
      }
    }
  },
  created() {
    this.fetchSections();
  }
};
</script>