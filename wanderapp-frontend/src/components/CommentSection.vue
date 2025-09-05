<template>
  <div class="comments-section">
    <h4 @click="commentsVisible = !commentsVisible" class="toggle-header">
      <span class="arrow" :class="{ rotated: commentsVisible }">▶</span>
      Kommentare ({{ comments.length }})
    </h4>
    
    <div v-if="commentsVisible">
      <ul v-if="comments.length" class="comment-list">
        <li v-for="comment in comments" :key="comment.id">
          <div class="comment-header">
            <strong>{{ comment.author.username }}:</strong>
            <button 
              v-if="canDelete(comment)" 
              @click="deleteComment(comment.id)" 
              class="btn-delete" 
              title="Kommentar löschen"
            >🗑️</button>
          </div>
          <p>{{ comment.text }}</p>
        </li>
      </ul>
      <p v-else><em>Noch keine Kommentare für diese Etappe.</em></p>

      <form @submit.prevent="submitComment" class="comment-form">
        <textarea 
          v-model="newCommentText" 
          placeholder="Dein Kommentar..." 
          rows="3" 
          required
        ></textarea>
        <button type="submit" :disabled="isSubmitting">
          {{ isSubmitting ? 'Sende...' : 'Senden' }}
        </button>
      </form>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '../api';
import { currentUser } from '../store';

const props = defineProps({
  stageId: {
    type: Number,
    required: true,
  },
  initialComments: {
    type: Array,
    required: true,
  },
  stageCreatorId: {
    type: Number,
    required: true,
  }
});

const emit = defineEmits(['comment-added']);

const comments = ref([...props.initialComments]);
const newCommentText = ref('');
const isSubmitting = ref(false);
const error = ref(null);
const commentsVisible = ref(false);

const canDelete = (comment) => {
  if (!currentUser.value) return false;
  // Admins (is_staff), the stage creator, or the comment author can delete
  return currentUser.value.is_staff || 
         currentUser.value.id === props.stageCreatorId || 
         currentUser.value.id === comment.author.id;
};

const deleteComment = async (commentId) => {
  if (window.confirm("Diesen Kommentar wirklich löschen?")) {
    try {
      await api.delete(`/comments/${commentId}/`);
      comments.value = comments.value.filter(c => c.id !== commentId);
      emit('comment-added'); // Notify parent to update counts if necessary
    } catch (err) {
      alert("Fehler beim Löschen des Kommentars.");
    }
  }
};

const submitComment = async () => {
  if (!newCommentText.value.trim()) return;
  isSubmitting.value = true;
  error.value = null;
  try {
    const payload = {
      stage: props.stageId,
      text: newCommentText.value,
    };
    const response = await api.post('/comments/', payload);
    comments.value.push(response.data);
    newCommentText.value = '';
    emit('comment-added');
  } catch (err) {
    error.value = "Fehler beim Senden des Kommentars.";
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.comments-section {
  margin-top: 1.5rem;
  border-top: 1px solid #f0f0f0;
  padding-top: 1.5rem;
}
.toggle-header {
  cursor: pointer;
  user-select: none;
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
}
.arrow {
  display: inline-block;
  transition: transform 0.2s ease-in-out;
  margin-right: 0.5rem;
}
.arrow.rotated {
  transform: rotate(90deg);
}
.comment-list {
  list-style: none;
  padding: 0;
}
.comment-list li {
  padding: 0.75rem;
  border-bottom: 1px solid #eee;
}
.comment-list li:last-child {
  border-bottom: none;
}
.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.comment-list p {
  margin: 0.25rem 0 0 0;
  white-space: pre-wrap;
  word-break: break-word;
}
.btn-delete {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  color: #aaa;
}
.btn-delete:hover {
  color: #dc3545;
}
.comment-form {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
textarea {
  width: 97%;
  padding: 0.8rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
  resize: vertical;
}
button {
  align-self: flex-end;
  padding: 0.5rem 1.5rem;
  background-color: #0d6efd;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
button:disabled {
  background-color: #ccc;
}
.error {
  color: red;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}
</style>