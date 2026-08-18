/**
 * Definição de rotas da API.
 * Camada VIEW: apenas extrai parâmetros da requisição,
 * delega ao controller e formata a resposta HTTP.
 * Erros são propagados (next) para o middleware centralizado.
 * ZERO lógica de negócio aqui.
 */
const { Router } = require('express');
const router = Router();

/**
 * Registra todas as rotas com seus respectivos controllers.
 * @param {Object} controllers
 * @param {import('../controllers/CheckoutController').CheckoutController} controllers.checkoutController
 * @param {import('../controllers/ReportController').ReportController} controllers.reportController
 * @param {import('../controllers/UserController').UserController} controllers.userController
 */
function registerRoutes(controllers) {
  const { checkoutController, reportController, userController } = controllers;

  // POST /api/checkout — fluxo de checkout de curso
  router.post('/api/checkout', async (req, res, next) => {
    try {
      const result = await checkoutController.execute({
        userName: req.body.usr,
        email: req.body.eml,
        password: req.body.pwd,
        courseId: req.body.c_id,
        cardNumber: req.body.card,
      });
      res.status(200).json({ msg: 'Sucesso', enrollment_id: result.enrollment_id });
    } catch (err) {
      next(err);
    }
  });

  // GET /api/admin/financial-report — relatório financeiro
  router.get('/api/admin/financial-report', async (req, res, next) => {
    try {
      const report = await reportController.generate();
      res.json(report);
    } catch (err) {
      next(err);
    }
  });

  // DELETE /api/users/:id — deletar usuário
  router.delete('/api/users/:id', async (req, res, next) => {
    try {
      const id = parseInt(req.params.id, 10);
      const result = await userController.delete(id);
      res.send(result.message);
    } catch (err) {
      next(err);
    }
  });

  return router;
}

module.exports = { registerRoutes };
