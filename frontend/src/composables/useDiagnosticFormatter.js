export function useDiagnosticFormatter() {
  const formatDurationMs = (diff) => {
    if (diff === null || diff === undefined || isNaN(diff)) return 'N/A';
    if (diff < 0) return '0s';

    const seconds = Math.floor((diff / 1000) % 60);
    const minutes = Math.floor((diff / (1000 * 60)) % 60);
    const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);

    if (hours > 0) return `${hours}h ${minutes}m ${seconds}s`;
    if (minutes > 0) return `${minutes}m ${seconds}s`;
    return `${seconds}s`;
  };

  const formatDuration = (startMs, endMs) => {
    if (!startMs || !endMs) return 'N/A';
    const start = new Date(startMs).getTime();
    const end = new Date(endMs).getTime();
    return formatDurationMs(end - start);
  };

  const formatDate = (isoDateStr) => {
    if (!isoDateStr) return 'N/A';
    const d = new Date(isoDateStr);
    return d.toLocaleString('pt-BR', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
  };

  return {
    formatDuration,
    formatDurationMs,
    formatDate,
  };
}
