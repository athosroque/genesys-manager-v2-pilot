<template>
  <div v-if="hasData" class="border-l-4 p-4 rounded-r-xl" :class="bannerClass">
    <div class="flex items-center gap-3">
      <span class="text-xl" v-if="isHumanTransfer">⚠️</span>
      <span class="text-xl" v-else>🤖</span>
      <div>
        <h4 class="text-sm font-bold" :class="titleTextClass">{{ bannerTitle }}</h4>
        <p class="text-xs mt-0.5" :class="descTextClass" v-html="bannerDescription"></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  details: {
    type: Object,
    default: () => ({})
  }
});

const hasData = computed(() => props.details?.participants && props.details.participants.length > 0);

// Avalia a origem observando os participantes antes do primeiro "agent" ou "user" no fluxo
const analysis = computed(() => {
  if (!hasData.value) return null;
  const parts = props.details.participants;
  
  let firstAgentIndex = -1;
  let firstAgent = null;
  
  for (let i = 0; i < parts.length; i++) {
    if (parts[i].purpose === 'agent' || parts[i].purpose === 'user') {
      firstAgentIndex = i;
      firstAgent = parts[i];
      break;
    }
  }

  // Se não tem agente, então nunca chegou num humano
  if (firstAgentIndex === -1) {
    return { isHumanTransfer: false, type: 'NO_AGENT' };
  }

  // Verifica se antes desse agente, existiu algum outro agente (transferência)
  // Como o JSON order geralmente é cronológico:
  let hasPreviousAgent = false;
  let previousAgent = null;
  
  for (let i = 0; i < firstAgentIndex; i++) {
    if (parts[i].purpose === 'agent' || parts[i].purpose === 'user') {
      hasPreviousAgent = true;
      previousAgent = parts[i];
      break;
    }
  }

  // Mas numa arquitetura Genesys mais precisa, buscaríamos na mesma "session" se veio de blind transfer.
  // Vamos usar a heurística de "houve agente antes de mim?"
  // Se for o último agente que atendeu a chamada, verifica quem transferiu.
  
  let totalAgents = parts.filter(p => p.purpose === 'agent' || p.purpose === 'user');
  
  if (totalAgents.length > 1) {
     return { 
       isHumanTransfer: true, 
       type: 'HUMAN_TRANSFER', 
       previousAgent: totalAgents[totalAgents.length - 2],
       currentAgent: totalAgents[totalAgents.length - 1]
     };
  } else {
     // Só tem 1 agente (ou o primeiro), vamos ver se veio de botflow/ivr
     const ivr = parts.find(p => p.purpose === 'botflow' || p.purpose === 'ivr');
     return {
       isHumanTransfer: false,
       type: 'BOT_TRANSFER',
       bot: ivr
     };
  }
});

const isHumanTransfer = computed(() => analysis.value?.isHumanTransfer);

const bannerClass = computed(() => {
  if (!analysis.value) return 'hidden';
  return isHumanTransfer.value ? 'bg-amber-50 border-amber-500' : 'bg-emerald-50 border-emerald-500';
});

const titleTextClass = computed(() => {
  return isHumanTransfer.value ? 'text-amber-900' : 'text-emerald-900';
});

const descTextClass = computed(() => {
  return isHumanTransfer.value ? 'text-amber-800' : 'text-emerald-800';
});

const bannerTitle = computed(() => {
  if (!analysis.value) return '';
  if (analysis.value.type === 'HUMAN_TRANSFER') return 'Origem do Atendimento: Transferência Humana (Não veio do Bot)';
  if (analysis.value.type === 'BOT_TRANSFER') return 'Origem do Atendimento: Direto do Bot / URA';
  return 'Origem: Não identificada';
});

const bannerDescription = computed(() => {
  if (!analysis.value) return '';
  if (analysis.value.type === 'HUMAN_TRANSFER') {
    const prev = analysis.value.previousAgent?.participantName || 'Outro Operador';
    const curr = analysis.value.currentAgent?.participantName || 'Operador Atual';
    return `O cliente foi atendido inicialmente por <b>${prev}</b> e depois transferido para <b>${curr}</b>.`;
  }
  if (analysis.value.type === 'BOT_TRANSFER') {
    const botName = analysis.value.bot?.participantName || 'Fluxo Automatizado';
    return `O cliente navegou pelo bot/ura <b>${botName}</b> e foi transbordado para a fila.`;
  }
  return 'Interação sem operador humano.';
});
</script>
