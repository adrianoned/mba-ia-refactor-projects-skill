/**
 * Configurações centralizadas da aplicação.
 * Todas as credenciais e valores sensíveis vêm de variáveis de ambiente.
 * Valores padrão são apenas para desenvolvimento local.
 */
require('dotenv').config();

const settings = {
  dbUser: process.env.DB_USER || 'dev_user',
  dbPass: process.env.DB_PASS || 'dev_pass',
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || 'pk_test_placeholder',
  smtpUser: process.env.SMTP_USER || 'dev@localhost',
  port: parseInt(process.env.PORT, 10) || 3000,
  nodeEnv: process.env.NODE_ENV || 'development',
};

module.exports = { settings };
