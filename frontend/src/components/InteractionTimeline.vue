<template>
  <div class="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
    <h3 class="text-base font-bold text-slate-800 mb-6 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <span class="text-xl">⏱️</span> Linha do Tempo da Interação
      </div>
      <!-- Botões de navegação -->
      <div class="flex gap-2" v-if="timelineBlocks.length > 0">
        <button @click="scrollLeft" type="button" class="w-7 h-7 flex items-center justify-center bg-slate-50 hover:bg-slate-200 text-slate-600 rounded-full transition-colors border border-slate-200 shadow-sm font-bold" title="Rolar para esquerda">
          ←
        </button>
        <button @click="scrollRight" type="button" class="w-7 h-7 flex items-center justify-center bg-slate-50 hover:bg-slate-200 text-slate-600 rounded-full transition-colors border border-slate-200 shadow-sm font-bold" title="Rolar para direita">
          →
        </button>
      </div>
    </h3>
    
    <div v-if="timelineBlocks.length === 0" class="text-sm text-slate-500">
      Nenhum evento detectado.
    </div>
    
    <!-- Modern Horizontal Timeline with Cards -->
    <div v-else class="flex overflow-x-auto pb-6 pt-2 px-2 -mx-2 gap-4 snap-x snap-mandatory custom-scrollbar" ref="scrollContainer">
      <div 
        v-for="(block, index) in timelineBlocks" 
        :key="index"
        class="flex-shrink-0 flex items-center snap-center relative group"
      >
        <!-- Card do Nó -->
        <div 
          class="w-64 bg-white rounded-xl border border-slate-200 p-4 shadow-sm group-hover:shadow-md transition-all relative flex flex-col justify-between"
          :class="[block.borderClass]"
        >
          <!-- Círculo Flutuante (Ícone) -->
          <div 
            class="absolute -top-4 -left-2 w-8 h-8 rounded-full flex items-center justify-center text-sm shadow-sm border bg-white"
            :class="block.iconColorClass"
          >
            {{ block.emoji }}
          </div>

          <!-- Duração no canto direito superior -->
          <div class="absolute -top-3 right-3 bg-slate-100 text-slate-600 border border-slate-200 text-[10px] font-bold px-2 py-0.5 rounded-full shadow-sm">
            {{ block.duration }}
          </div>

          <div class="mt-2">
            <p class="text-[10px] font-semibold uppercase tracking-wider mb-1" :class="block.textColorClass">{{ block.typeLabel }}</p>
            <h4 class="text-sm font-bold text-slate-800 truncate" :title="block.title">{{ block.title }}</h4>
            <p class="text-xs text-slate-500 mt-1 line-clamp-2" :title="block.subtitle">{{ block.subtitle }}</p>
          </div>

          <div v-if="block.tags && block.tags.length > 0" class="mt-3 flex flex-wrap gap-1">
            <span 
              v-for="(tag, tIdx) in block.tags" :key="tIdx"
              class="flex items-center gap-1 text-[9px] font-bold px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200 cursor-help transition-colors hover:bg-slate-200"
              :class="tag.class"
              :title="tag.tooltip || ''"
            >
              {{ tag.label }}
              <span v-if="tag.tooltip" class="inline-flex items-center justify-center w-3 h-3 rounded-full bg-slate-300 text-slate-700 text-[8px] leading-none opacity-80">?</span>
            </span>
          </div>
        </div>

        <!-- Conector -->
        <div v-if="index !== timelineBlocks.length - 1" class="w-8 h-1 bg-slate-200 mx-1 shrink-0 rounded-full"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import { useDiagnosticFormatter } from '../composables/useDiagnosticFormatter';

const props = defineProps({
  details: {
    type: Object,
    default: () => ({})
  }
});

const { formatDuration, formatDurationMs } = useDiagnosticFormatter();

const scrollContainer = ref(null);

const scrollLeft = () => {
  if (scrollContainer.value) {
    scrollContainer.value.scrollBy({ left: -320, behavior: 'smooth' });
  }
};

const scrollRight = () => {
  if (scrollContainer.value) {
    scrollContainer.value.scrollBy({ left: 320, behavior: 'smooth' });
  }
};

const timelineBlocks = computed(() => {
  if (!props.details?.participants) return [];
  const blocks = [];
  
  props.details.participants.forEach(p => {
    // 1. WORKFLOW (Orquestrador)
    if (p.purpose === 'workflow') {
      p.sessions?.forEach(s => {
        const flowName = s.flow?.flowName || p.participantName || 'Workflow';
        const tFlow = s.metrics?.find(m => m.name === 'tFlow');
        const oMessageCount = s.metrics?.find(m => m.name === 'oMessageCount');
        const outcomes = s.flow?.outcomes || [];
        
        let subtitle = `Fluxo: ${s.flow?.flowType || 'Desconhecido'}`;
        if (s.flow?.transferTargetName) {
          subtitle = `Transfere para: ${s.flow.transferTargetName}`;
        }
        
        const tags = [];
        if (s.flow?.flowVersion) tags.push({ label: `v${s.flow.flowVersion}` });
        if (oMessageCount) tags.push({ label: `${oMessageCount.value} msgs` });
        if (outcomes.length > 0) {
          const outcomeVal = outcomes[0].flowOutcomeValue;
          tags.push({ 
            label: outcomeVal.includes(':') ? outcomeVal.split(':')[1] : outcomeVal, 
            class: outcomeVal.includes('SUCCESS') ? '!bg-green-50 !text-green-700 !border-green-200' : ''
          });
        }
        
        blocks.push({
          typeLabel: 'Orquestrador',
          title: flowName,
          subtitle: subtitle,
          emoji: '⚙️',
          borderClass: 'border-l-4 border-l-blue-400',
          iconColorClass: 'text-blue-500 border-blue-200',
          textColorClass: 'text-blue-600',
          duration: tFlow ? formatDurationMs(tFlow.value) : formatDuration(s.segments?.[0]?.segmentStart, s.segments?.[s.segments.length-1]?.segmentEnd),
          tags: tags
        });
      });
    }
    
    // 2. BOTFLOW / IVR
    if (p.purpose === 'botflow' || p.purpose === 'ivr') {
      p.sessions?.forEach(s => {
        const flowName = s.flow?.flowName || p.participantName || 'Bot/URA';
        const tFlow = s.metrics?.find(m => m.name === 'tFlow' || m.name === 'tIvr');
        
        const tags = [];
        if (s.flow?.flowVersion) tags.push({ label: `v${s.flow.flowVersion}` });
        if (s.flow?.exitReason) tags.push({ label: `Exit: ${s.flow.exitReason}` });
        
        blocks.push({
          typeLabel: p.purpose === 'botflow' ? 'Botflow' : 'URA',
          title: flowName,
          subtitle: `Iniciado via ${s.flow?.entryType || 'direto'}`,
          emoji: '🤖',
          borderClass: 'border-l-4 border-l-purple-400',
          iconColorClass: 'text-purple-500 border-purple-200',
          textColorClass: 'text-purple-600',
          duration: tFlow ? formatDurationMs(tFlow.value) : formatDuration(s.segments?.[0]?.segmentStart, s.segments?.[s.segments.length-1]?.segmentEnd),
          tags: tags
        });
      });
    }
    
    // 3. ACD (Fila)
    if (p.purpose === 'acd') {
      let tAcd = null;
      let qName = p.participantName || 'Fila';
      p.sessions?.forEach(s => {
        const metric = s.metrics?.find(m => m.name === 'tAcd');
        if (metric) tAcd = metric.value;
      });
      
      const tags = [];
      p.sessions?.forEach(s => {
        if (s.flow?.flowName) tags.push({ label: `Fluxo: ${s.flow.flowName}` });
      });

      blocks.push({
        typeLabel: 'Fila de Atendimento',
        title: qName,
        subtitle: 'Aguardando distribuição para agente',
        emoji: '⏳',
        borderClass: 'border-l-4 border-l-yellow-400',
        iconColorClass: 'text-yellow-500 border-yellow-200',
        textColorClass: 'text-yellow-600',
        duration: tAcd ? formatDurationMs(tAcd) : '0s',
        tags: tags
      });
    }
    
    // 4. AGENT / USER
    if (p.purpose === 'agent' || p.purpose === 'user') {
      let tTalk = 0;
      let tHeld = 0;
      let tAcw = 0;
      let tHandle = 0;
      let holdCount = 0;
      let wrapupCode = null;
      
      p.sessions?.forEach(s => {
        const mTalk = s.metrics?.find(m => m.name === 'tTalkComplete' || m.name === 'tTalk');
        const mHeld = s.metrics?.find(m => m.name === 'tHeldComplete' || m.name === 'tHeld');
        const mAcw = s.metrics?.find(m => m.name === 'tAcw');
        const mHandle = s.metrics?.find(m => m.name === 'tHandle');
        
        if (mTalk) tTalk += mTalk.value;
        if (mHeld) tHeld += mHeld.value;
        if (mAcw) tAcw += mAcw.value;
        if (mHandle) tHandle += mHandle.value;
        
        s.segments?.forEach(seg => {
          if (seg.segmentType === 'hold') holdCount++;
          if (seg.segmentType === 'wrapup' && seg.wrapUpCode) wrapupCode = seg.wrapUpCode;
        });
      });
      
      const tags = [];
      if (tTalk > 0) tags.push({ label: `Fala: ${formatDurationMs(tTalk)}`, tooltip: 'Tempo ativo de conversa. Para interações digitais (como WhatsApp), o valor é 0s pois a plataforma considera "fala" apenas interações por voz.' });
      if (tHeld > 0) tags.push({ label: `Espera: ${formatDurationMs(tHeld)} (${holdCount}x)`, tooltip: `O atendente colocou o cliente em espera (pausou a interação) ${holdCount} vezes, totalizando ${formatDurationMs(tHeld)}.` });
      if (tAcw > 0) tags.push({ label: `ACW: ${formatDurationMs(tAcw)}`, tooltip: 'After Call Work (Tabulação). Tempo que o agente passou na tela de tabulação preenchendo o motivo do contato e notas após finalizar a conversa com o cliente.' });
      if (wrapupCode) {
        const isTimeout = wrapupCode.includes('TIMEOUT');
        tags.push({ 
          label: wrapupCode, 
          class: isTimeout ? '!bg-red-50 !text-red-700 !border-red-200' : '!bg-slate-700 !text-white',
          tooltip: 'Código de Finalização (Wrap-up Code) inserido pelo atendente ou pelo sistema.'
        });
      }
      
      blocks.push({
        typeLabel: 'Atendimento Humano',
        title: p.participantName || 'Agente',
        subtitle: `Atendimento Total: ${tHandle > 0 ? formatDurationMs(tHandle) : '0s'}`,
        emoji: '🗣️',
        borderClass: 'border-l-4 border-l-emerald-400',
        iconColorClass: 'text-emerald-500 border-emerald-200',
        textColorClass: 'text-emerald-600',
        duration: tHandle > 0 ? formatDurationMs(tHandle) : '0s',
        tags: tags
      });
    }
  });

  return blocks;
});
</script>

<style scoped>
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 #f1f5f9;
}
.custom-scrollbar::-webkit-scrollbar {
  height: 8px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: #f1f5f9; 
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1; 
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #94a3b8; 
}
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
