<template>
  <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
    <!-- Canal & Sentido -->
    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
      <span class="text-xs text-slate-500 font-semibold uppercase">Canal & Sentido</span>
      <div class="mt-1 flex items-center gap-2">
        <span 
          class="px-2.5 py-0.5 rounded-full text-xs font-bold"
          :class="channelBadgeClass"
        >
          {{ channelName.toUpperCase() }}
        </span>
        <span class="text-sm font-medium text-slate-700 capitalize">
          {{ directionDisplay }}
        </span>
      </div>
      <p v-if="messageCount > 0" class="text-xs text-slate-500 mt-2 font-medium">
        <span class="inline-block bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded mr-1 text-[10px]">💬</span>
        {{ messageCount }} mensagens trocadas
      </p>
    </div>

    <!-- Cliente & Destino -->
    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm relative">
      <span class="text-xs text-slate-500 font-semibold uppercase">Cliente / Destino</span>
      <p class="mt-1 text-sm font-bold text-slate-800 truncate">{{ clientName || 'Desconhecido' }}</p>
      <div class="flex items-center gap-2">
        <p class="text-xs text-slate-500">{{ clientNumber || 'N/A' }} <span v-if="dnis">-> {{ dnis }}</span></p>
        <span v-if="externalTag" class="text-[10px] bg-indigo-50 text-indigo-700 px-1.5 py-0.5 rounded font-mono font-bold border border-indigo-100" title="CPF Cliente">
          🪪 CPF: {{ externalTag }}
        </span>
      </div>
    </div>

    <!-- Duração Total -->
    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
      <span class="text-xs text-slate-500 font-semibold uppercase">Duração Total</span>
      <p class="mt-1 text-lg font-extrabold text-slate-900">{{ durationFormatted }}</p>
      <p class="text-xs text-slate-400" v-if="startTimeFormatted">Início: {{ startTimeFormatted }}</p>
    </div>

    <!-- Desconexão -->
    <div class="bg-white p-4 rounded-xl border border-slate-200 shadow-sm relative">
      <div class="flex items-center justify-between">
        <span class="text-xs text-slate-500 font-semibold uppercase">Desconexão</span>

        <!-- Botão com interrogação e tooltip explicativo -->
        <div class="relative group" @mouseleave="isInfoOpen = false">
          <button 
            type="button"
            @click="isInfoOpen = !isInfoOpen"
            class="w-5 h-5 rounded-full bg-slate-100 hover:bg-indigo-100 text-slate-500 hover:text-indigo-600 flex items-center justify-center text-xs font-bold transition-all cursor-help border border-slate-200 hover:border-indigo-300 shadow-2xs"
            title="Clique ou passe o mouse para entender os tipos de desconexão"
          >
            ?
          </button>

          <!-- Popover Informativo -->
          <div 
            class="absolute right-0 top-full mt-2 w-80 sm:w-96 p-4 bg-slate-900/95 backdrop-blur-sm text-white rounded-xl shadow-2xl border border-slate-700/80 text-xs z-50 invisible group-hover:visible opacity-0 group-hover:opacity-100 transition-all duration-200 pointer-events-none group-hover:pointer-events-auto"
            :class="{ '!visible !opacity-100 !pointer-events-auto': isInfoOpen }"
          >
            <!-- Seta indicadora -->
            <div class="absolute -top-1.5 right-1.5 w-3 h-3 bg-slate-900 border-t border-l border-slate-700 rotate-45"></div>

            <div class="flex items-center justify-between pb-2 mb-2.5 border-b border-slate-800">
              <h4 class="font-bold text-slate-100 flex items-center gap-1.5 text-xs">
                <span>ℹ️</span> Tipos de Desconexão (Genesys)
              </h4>
              <span v-if="disconnectType" class="text-[10px] px-2 py-0.5 rounded font-mono uppercase bg-slate-800 text-amber-300 border border-slate-700">
                Atual: {{ disconnectType }}
              </span>
            </div>

            <p class="text-[11px] text-slate-400 mb-3 leading-relaxed">
              O campo <code class="text-indigo-300 bg-slate-800 px-1 py-0.5 rounded">disconnectType</code> indica a origem ou o motivo do encerramento desta perna da conversa:
            </p>

            <div class="space-y-2 max-h-72 overflow-y-auto pr-1">
              <div 
                v-for="item in disconnectTypesList" 
                :key="item.type"
                class="p-2.5 rounded-lg transition-colors border"
                :class="item.type === (disconnectType || '').toLowerCase() ? 'bg-indigo-950/80 border-indigo-500/80 ring-1 ring-indigo-500/40' : 'bg-slate-800/50 border-slate-800 hover:bg-slate-800/80'"
              >
                <div class="flex items-center justify-between mb-1">
                  <span class="font-bold font-mono text-[11px] text-white flex items-center gap-1.5">
                    <span class="w-1.5 h-1.5 rounded-full" :class="item.dotClass"></span>
                    {{ item.type }}
                  </span>
                  <span class="text-[10px] font-medium text-slate-400">{{ item.label }}</span>
                </div>
                <p class="text-[11px] text-slate-300 leading-snug">{{ item.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <p class="mt-1">
        <span 
          class="px-2 py-0.5 rounded text-xs font-bold inline-block cursor-help"
          :class="disconnectBadgeClass"
          :title="getDisconnectTypeTooltip(disconnectType)"
        >
          {{ disconnectType || 'Ativa / Não Desconectada' }}
        </span>
      </p>
      <p class="text-xs text-slate-400 mt-1 truncate" :title="disconnectReason">{{ disconnectReason || '-' }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useDiagnosticFormatter } from '../composables/useDiagnosticFormatter';

const isInfoOpen = ref(false);

const disconnectTypesList = [
  {
    type: 'client',
    label: 'Aplicação Local',
    dotClass: 'bg-emerald-400',
    description: 'Encerramento solicitado pelo software cliente local. No agente, significa que ele clicou em "Desligar". No bot/API externa, o script solicitou o término.'
  },
  {
    type: 'peer',
    label: 'Ponta Remota',
    dotClass: 'bg-sky-400',
    description: 'A outra ponta desligou primeiro. Ex: o cliente/consumidor final bateu o telefone ou encerrou a chamada no seu aparelho.'
  },
  {
    type: 'system',
    label: 'Sistema Genesys',
    dotClass: 'bg-amber-400',
    description: 'O próprio sistema encerrou a interação. Ex: timeout de URA/fluxo, fila sem agentes disponíveis ou limite máximo de duração.'
  },
  {
    type: 'transfer',
    label: 'Transferência',
    dotClass: 'bg-blue-400',
    description: 'A perna foi finalizada porque a interação foi transferida com sucesso para outra fila, fluxo ou atendente.'
  },
  {
    type: 'endpoint',
    label: 'Dispositivo SIP / Hardware',
    dotClass: 'bg-purple-400',
    description: 'O dispositivo SIP, WebRTC Phone ou telefone físico encerrou a sessão de áudio diretamente.'
  },
  {
    type: 'error',
    label: 'Falha / Queda Técnica',
    dotClass: 'bg-rose-500',
    description: 'Queda inesperada devido a erro de sinalização SIP, perda de conexão de rede ou falha de infraestrutura.'
  },
  {
    type: 'spam',
    label: 'Spam / DND',
    dotClass: 'bg-slate-400',
    description: 'Chamada encerrada ou rejeitada por políticas de bloqueio de spam ou modo Não Perturbe.'
  }
];

const getDisconnectTypeTooltip = (type) => {
  if (!type) return 'Interação ativa ou sem término registrado';
  const found = disconnectTypesList.find(i => i.type.toLowerCase() === type.toLowerCase());
  return found ? `${found.label}: ${found.description}` : type;
};

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

const { formatDuration, formatDate } = useDiagnosticFormatter();

// Funções utilitárias para extrair dados com segurança
const getFirstSession = () => {
  const parts = props.details?.participants || [];
  for (const p of parts) {
    if (p.sessions && p.sessions.length > 0) {
      return p.sessions[0];
    }
  }
  return {};
};

const getCustomerParticipant = () => {
  const parts = props.details?.participants || [];
  return parts.find(p => p.purpose === 'customer' || p.purpose === 'external');
};

const getLastSegment = () => {
  const parts = props.details?.participants || [];
  for (let i = parts.length - 1; i >= 0; i--) {
    const p = parts[i];
    if (p.sessions) {
      for (let j = p.sessions.length - 1; j >= 0; j--) {
        const s = p.sessions[j];
        if (s.segments) {
          for (let k = s.segments.length - 1; k >= 0; k--) {
            const seg = s.segments[k];
            if (seg.disconnectType) return seg;
          }
        }
      }
    }
  }
  return {};
};

const session = computed(() => getFirstSession());
const customer = computed(() => getCustomerParticipant());
const lastSegment = computed(() => getLastSegment());

const channelName = computed(() => session.value.mediaType || 'Desconhecido');
const direction = computed(() => session.value.direction || 'unknown');
const directionDisplay = computed(() => {
  if (direction.value === 'inbound') return 'Inbound (Receptivo)';
  if (direction.value === 'outbound') return 'Outbound (Ativo)';
  return direction.value;
});

const channelBadgeClass = computed(() => {
  const ch = channelName.value.toLowerCase();
  if (ch === 'voice') return 'bg-blue-100 text-blue-800';
  if (ch === 'message' || ch === 'whatsapp') return 'bg-green-100 text-green-800';
  if (ch === 'email') return 'bg-yellow-100 text-yellow-800';
  return 'bg-gray-100 text-gray-800';
});

const clientName = computed(() => customer.value?.participantName);
const clientNumber = computed(() => customer.value?.sessions?.[0]?.ani || session.value.ani || session.value.addressFrom);
const dnis = computed(() => session.value.dnis || session.value.addressTo);
const externalTag = computed(() => props.details.externalTag);

const messageCount = computed(() => {
  if (channelName.value !== 'message') return 0;
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

const durationFormatted = computed(() => {
  return formatDuration(props.details.conversationStart, props.details.conversationEnd);
});
const startTimeFormatted = computed(() => formatDate(props.details.conversationStart));

const disconnectType = computed(() => lastSegment.value.disconnectType);
const disconnectReason = computed(() => lastSegment.value.disconnectReason);

const disconnectBadgeClass = computed(() => {
  const type = (disconnectType.value || '').toLowerCase();
  if (type === 'client' || type === 'peer') return 'bg-slate-100 text-slate-800';
  if (type === 'transfer') return 'bg-blue-100 text-blue-800';
  if (type === 'system' || type === 'error') return 'bg-red-100 text-red-800';
  return 'bg-gray-100 text-gray-800';
});
</script>
