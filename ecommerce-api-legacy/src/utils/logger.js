/**
 * Logger minimalista com níveis e timestamp.
 * Sem dependências externas — substitui console.* espalhado.
 */
const LEVELS = { debug: 0, info: 1, warn: 2, error: 3 };
const currentLevel = LEVELS[(process.env.LOG_LEVEL || 'info').toLowerCase()] ?? LEVELS.info;

function write(level, method, args) {
  if (LEVELS[level] < currentLevel) return;
  const ts = new Date().toISOString();
  console[method](`[${ts}] [${level.toUpperCase()}]`, ...args);
}

const logger = {
  info: (...args) => write('info', 'log', args),
  warn: (...args) => write('warn', 'warn', args),
  error: (...args) => write('error', 'error', args),
};

module.exports = { logger };
