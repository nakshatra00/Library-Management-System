<!-- AddSection.vue -->
<template>
  <div class="container mt-5">
    <h2>Add New Section</h2>
    <form @submit.prevent="addSection">
      <div class="mb-3">
        <label for="sectionName" class="form-label">Section Name</label>
        <input type="text" class="form-control" id="sectionName" v-model="newSection.name" required>
      </div>
      <div class="mb-3">
        <label for="sectionDescription" class="form-label">Description</label>
        <textarea class="form-control" id="sectionDescription" v-model="newSection.description" required></textarea>
      </div>
      <button type="submit" class="btn btn-primary" :disabled="!isValidSection">Add Section</button>
    </form>
  </div>
</template>

<script>
export default {
  name: 'AddSection',
  data: function() {
    return {
      newSection: {
        name: '',
        description: ''
      }
    };
  },
  computed: {
    isValidSection: function() {
      return this.newSection.name.trim() !== '' && this.newSection.description.trim() !== '';
    }
  },
  methods: {
    addSection: async function() {
      if (!this.isValidSection) return;
      try {
        await this.$axios.post('/api/sections', this.newSection);
        this.$toast.success('Section added successfully');
        this.newSection.name = '';
        this.newSection.description = '';
        // Optionally, redirect to the sections list
        this.$router.push('/sections');
      } catch (error) {
        this.$toast.error(error.response?.data?.message || 'Failed to add section');
      }
    }
  }
};
</script>