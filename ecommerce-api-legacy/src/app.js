/**
 * Entry point — Composition Root da aplicação.
 * Responsabilidades: criar app Express, inicializar DB,
 * instanciar models/controllers com injeção de dependência,
 * registrar middlewares e rotas.
 *
 * ZERO lógica de negócio. ZERO credenciais hardcoded.
 */
const express = require('express');
const { settings } = require('./config/settings');
const { initDatabase } = require('./config/database');
const { errorHandler } = require('./middlewares/errorHandler');
const { registerRoutes } = require('./routes/index');

// Models
const { UserModel } = require('./models/User');
const { CourseModel } = require('./models/Course');
const { EnrollmentModel } = require('./models/Enrollment');
const { PaymentModel } = require('./models/Payment');
const { AuditLogModel } = require('./models/AuditLog');

// Controllers
const { CheckoutController } = require('./controllers/CheckoutController');
const { ReportController } = require('./controllers/ReportController');
const { UserController } = require('./controllers/UserController');

function createApp() {
  const app = express();
  app.use(express.json());

  // Inicializa banco de dados
  const db = initDatabase();

  // Instancia models (cada um recebe a conexão via construtor — DI)
  const userModel = new UserModel(db);
  const courseModel = new CourseModel(db);
  const enrollmentModel = new EnrollmentModel(db);
  const paymentModel = new PaymentModel(db);
  const auditLogModel = new AuditLogModel(db);

  // Instancia controllers (dependências injetadas via construtor)
  const checkoutController = new CheckoutController(
    userModel, courseModel, enrollmentModel, paymentModel, auditLogModel
  );
  const reportController = new ReportController(
    courseModel, enrollmentModel, paymentModel, userModel
  );
  const userController = new UserController(userModel);

  // Registra rotas
  const routes = registerRoutes({ checkoutController, reportController, userController });
  app.use(routes);

  // Middleware de erro (deve ser o último)
  app.use(errorHandler);

  return app;
}

// Bootstrap
if (require.main === module) {
  const app = createApp();
  app.listen(settings.port, () => {
    console.log(`LMS API rodando na porta ${settings.port}...`);
  });
}

module.exports = { createApp };
