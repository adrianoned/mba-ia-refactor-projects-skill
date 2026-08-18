/**
 * Middleware centralizado de tratamento de erros.
 * Captura erros não tratados e retorna resposta padronizada.
 */
const { logger } = require('../utils/logger');

function errorHandler(err, req, res, _next) {
  const statusCode = err.statusCode || 500;
  const message = err.message || 'Erro interno do servidor';

  // Log estruturado do erro (sem dados sensíveis)
  logger.error(`${req.method} ${req.path}: ${message}`);

  if (statusCode === 500) {
    // Em produção, não expor detalhes internos
    res.status(500).send('Erro DB');
  } else {
    res.status(statusCode).send(message);
  }
}

module.exports = { errorHandler };
