/**
 * Constantes de domínio compartilhadas.
 * Evita magic strings espalhadas pelo código.
 */
const PAYMENT_STATUS = {
  PAID: 'PAID',
  DENIED: 'DENIED',
};

module.exports = { PAYMENT_STATUS };
