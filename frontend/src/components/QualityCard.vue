<template>
  <div>
    <!-- WebRTC Card -->
    <div v-if="hasWebRTC" class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
      <h3 class="text-base font-bold text-slate-800 mb-4 flex items-center gap-2">
        <span class="text-xl">🌐</span> Telefonia & Qualidade WebRTC
      </h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        <!-- Lado Esquerdo: Servidor e SIP -->
        <div class="space-y-4">
          <div>
            <span class="text-xs text-slate-500 font-semibold uppercase">Servidor Edge AWS</span>
            <div class="mt-1 flex items-center gap-2">
              <code class="text-sm bg-slate-100 px-2 py-1 rounded text-slate-700 truncate w-64">{{ edgeId || 'N/A' }}</code>
              <button v-if="edgeId" @click="copyToClipboard(edgeId)" class="text-blue-600 text-sm hover:underline" title="Copiar Edge ID">Copiar</button>
            </div>
          </div>
          
          <div>
            <span class="text-xs text-slate-500 font-semibold uppercase">SIP Call-ID (Operadora)</span>
            <div class="mt-1 flex items-center gap-2">
              <code class="text-sm bg-slate-100 px-2 py-1 rounded text-slate-700 truncate w-64">{{ sipCallId || 'N/A' }}</code>
              <button v-if="sipCallId" @click="copyToClipboard(sipCallId)" class="text-blue-600 text-sm hover:underline" title="Copiar SIP Call-ID">Copiar</button>
            </div>
          </div>
          
          <div v-if="provider">
            <span class="text-xs text-slate-500 font-semibold uppercase">Provedor / Endereço</span>
            <p class="mt-1 text-sm text-slate-700">{{ provider }} - {{ address }}</p>
          </div>
        </div>
        
        <!-- Lado Direito: Qualidade de Áudio -->
        <div class="border-t md:border-t-0 md:border-l border-slate-200 pt-4 md:pt-0 md:pl-6 space-y-3">
          
          <div class="flex justify-between items-center">
            <span class="text-sm font-semibold text-slate-600">Qualidade MOS:</span>
            <span class="font-bold px-2 py-1 rounded" :class="mosClass">
              {{ minMos }} / 5.0
            </span>
          </div>
          
          <div class="flex justify-between items-center">
            <span class="text-sm font-semibold text-slate-600">R-Factor:</span>
            <span class="font-bold text-slate-800">{{ minRFactor }} / 100</span>
          </div>
          
          <div class="flex justify-between items-center">
            <span class="text-sm font-semibold text-slate-600">Latência Máxima:</span>
            <span class="font-bold px-2 py-1 rounded" :class="latencyClass">
              {{ maxLatencyMs }} ms
            </span>
          </div>
          
          <div class="flex justify-between items-center border-t border-slate-100 pt-2 mt-2">
            <span class="text-sm font-semibold text-slate-600">Pacotes Descartados:</span>
            <span class="font-bold flex items-center gap-2" :class="discardedClass">
              <span v-if="discardedPackets > 0">⚠️</span>
              <span v-else>✅</span>
              {{ discardedPackets }} pacotes perdidos na rede
            </span>
          </div>
          
        </div>
      </div>
    </div>

    <!-- Messaging/Digital Card -->
    <div v-else-if="hasMessaging" class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
      <h3 class="text-base font-bold text-slate-800 mb-4 flex items-center gap-2">
        <span class="text-xl">📱</span> Métricas de Mensageria
      </h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="space-y-4">
          <div>
            <span class="text-xs text-slate-500 font-semibold uppercase">Total de Mensagens Trocadas</span>
            <div class="mt-1 flex items-center gap-2 font-bold text-lg text-slate-800">
              {{ totalMessages }} <span class="text-sm text-slate-400 font-medium ml-1">mensagens na sessão</span>
            </div>
          </div>
          <div>
            <span class="text-xs text-slate-500 font-semibold uppercase">Provedor de Mensageria</span>
            <p class="mt-1 text-sm font-medium text-slate-700 bg-slate-100 px-2 py-1 rounded inline-block">
              {{ msgProvider || 'Desconhecido' }}
            </p>
          </div>
        </div>

        <div class="border-t md:border-t-0 md:border-l border-slate-200 pt-4 md:pt-0 md:pl-6 space-y-3">
          <div class="flex flex-col gap-1">
            <span class="text-sm font-semibold text-slate-600">Tempo de Resposta do Agente (TMA):</span>
            <span class="font-bold text-indigo-700 text-lg">
              {{ agentResponseTimeFormatted }}
            </span>
            <p class="text-[10px] text-slate-400">Tempo total de resposta ativa pelo agente durante a conversa.</p>
          </div>
          
          <div class="flex justify-between items-center border-t border-slate-100 pt-3 mt-2">
            <span class="text-sm font-semibold text-slate-600 flex items-center gap-1 cursor-help" title="Mecânica de Roteamento: Indica a forma como a interação chegou ao agente. 'Manual' significa que houve transferência direta, ação humana ou roteamento direcionado, não passando pela fila automática tradicional.">
              Mecânica de Roteamento:
              <span class="inline-flex items-center justify-center w-3 h-3 rounded-full bg-slate-200 text-slate-500 text-[9px] font-bold">?</span>
            </span>
            <span class="font-bold px-2 py-1 rounded bg-blue-50 text-blue-700 text-xs">
              {{ routingMethod }}
            </span>
          </div>
        </div>
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
  },
  calls: {
    type: Object,
    default: () => ({})
  }
});

// Busca a primeira sessão com mediaEndpointStats
const getMediaStats = () => {
  const parts = props.details?.participants || [];
  for (const p of parts) {
    if (p.sessions) {
      for (const s of p.sessions) {
        if (s.mediaEndpointStats && s.mediaEndpointStats.length > 0) {
          return { session: s, stats: s.mediaEndpointStats[0] };
        }
      }
    }
  }
  return null;
};

// Computeds para Messaging
import { useDiagnosticFormatter } from '../composables/useDiagnosticFormatter';
const { formatDurationMs } = useDiagnosticFormatter();

const hasMessaging = computed(() => {
  const parts = props.details?.participants || [];
  for (const p of parts) {
    if (p.sessions) {
      for (const s of p.sessions) {
        if (s.mediaType === 'message' || s.mediaType === 'whatsapp') return true;
      }
    }
  }
  return false;
});

const totalMessages = computed(() => {
  let total = 0;
  const parts = props.details?.participants || [];
  parts.forEach(p => {
    p.sessions?.forEach(s => {
      const mc = s.metrics?.find(m => m.name === 'oMessageCount');
      if (mc) total += mc.value;
    });
  });
  return total;
});

const msgProvider = computed(() => {
  const parts = props.details?.participants || [];
  for (const p of parts) {
    if (p.sessions) {
      for (const s of p.sessions) {
        if (s.provider) return s.provider;
      }
    }
  }
  return null;
});

const agentResponseTimeFormatted = computed(() => {
  let responseTime = 0;
  const parts = props.details?.participants || [];
  for (const p of parts) {
    if (p.purpose === 'agent' || p.purpose === 'user') {
      p.sessions?.forEach(s => {
        const mrt = s.metrics?.find(m => m.name === 'tAgentResponseTime');
        if (mrt) responseTime += mrt.value;
      });
    }
  }
  return responseTime > 0 ? formatDurationMs(responseTime) : 'N/A';
});

const routingMethod = computed(() => {
  const parts = props.details?.participants || [];
  for (const p of parts) {
    if (p.purpose === 'agent' || p.purpose === 'user') {
      for (const s of p.sessions || []) {
        if (s.usedRouting) return s.usedRouting;
      }
    }
  }
  return 'Standard (Automático)';
});

const mediaData = computed(() => getMediaStats());
const hasWebRTC = computed(() => !!mediaData.value);

const stats = computed(() => mediaData.value?.stats || {});
const session = computed(() => mediaData.value?.session || {});

const edgeId = computed(() => session.value.edgeId);
const sipCallId = computed(() => session.value.protocolCallId);

const provider = computed(() => {
  if (props.calls?.participants && props.calls.participants.length > 0) {
     return props.calls.participants[0].provider;
  }
  return null;
});

const address = computed(() => {
  if (props.calls?.participants && props.calls.participants.length > 0) {
     return props.calls.participants[0].address;
  }
  return null;
});

const minMos = computed(() => stats.value.minMos || 'N/A');
const minRFactor = computed(() => stats.value.minRFactor || 'N/A');
const maxLatencyMs = computed(() => stats.value.maxLatencyMs ?? 'N/A');
const discardedPackets = computed(() => stats.value.discardedPackets || 0);

const mosClass = computed(() => {
  if (minMos.value === 'N/A') return 'bg-gray-100 text-gray-800';
  const val = parseFloat(minMos.value);
  if (val >= 4.3) return 'bg-green-100 text-green-800';
  if (val >= 4.0) return 'bg-yellow-100 text-yellow-800';
  return 'bg-red-100 text-red-800';
});

const latencyClass = computed(() => {
  if (maxLatencyMs.value === 'N/A') return 'bg-gray-100 text-gray-800';
  const val = parseInt(maxLatencyMs.value);
  if (val < 100) return 'bg-green-100 text-green-800';
  if (val <= 200) return 'bg-yellow-100 text-yellow-800';
  return 'bg-red-100 text-red-800';
});

const discardedClass = computed(() => {
  return discardedPackets.value > 0 ? 'text-red-600 bg-red-50 px-2 py-1 rounded animate-pulse' : 'text-green-600';
});

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text);
};
</script>
