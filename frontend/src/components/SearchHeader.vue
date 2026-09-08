<template>
  <div class="bg-white p-4 rounded-xl shadow-sm border border-slate-200 flex flex-col md:flex-row gap-4 items-center">
    <div class="w-full md:w-auto text-slate-700 font-bold flex-shrink-0">
      🔍 Buscar Interação
    </div>
    <input 
      type="text" 
      v-model="conversationId"
      @keyup.enter="handleSearch"
      placeholder="Cole o conversationId aqui..." 
      class="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 w-full"
    />
    <button 
      @click="handleSearch"
      :disabled="isLoading || !conversationId.trim()"
      class="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed w-full md:w-auto whitespace-nowrap"
    >
      <span v-if="isLoading">Buscando...</span>
      <span v-else>Auditar Interação</span>
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  isLoading: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['search']);
const conversationId = ref('');

const handleSearch = () => {
  if (conversationId.value.trim() && !props.isLoading) {
    emit('search', conversationId.value.trim());
  }
};
</script>
