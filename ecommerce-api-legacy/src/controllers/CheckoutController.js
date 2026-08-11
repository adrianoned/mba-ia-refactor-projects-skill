/**
 * CheckoutController — orquestra o fluxo de checkout de curso.
 * Contém a lógica de negócio pura, sem dependência HTTP (req/res).
 */
const { settings } = require('../config/settings');

/** Prefixo Visa — usado na simulação de autorização de pagamento */
const VISA_CARD_PREFIX = '4';

class CheckoutController {
  /**
   * @param {import('../models/User').UserModel} userModel
   * @param {import('../models/Course').CourseModel} courseModel
   * @param {import('../models/Enrollment').EnrollmentModel} enrollmentModel
   * @param {import('../models/Payment').PaymentModel} paymentModel
   * @param {import('../models/AuditLog').AuditLogModel} auditLogModel
   */
  constructor(userModel, courseModel, enrollmentModel, paymentModel, auditLogModel) {
    this.userModel = userModel;
    this.courseModel = courseModel;
    this.enrollmentModel = enrollmentModel;
    this.paymentModel = paymentModel;
    this.auditLogModel = auditLogModel;
  }

  /**
   * Executa o fluxo completo de checkout:
   * 1. Valida campos obrigatórios
   * 2. Busca/valida curso
   * 3. Busca ou cria usuário
   * 4. Processa pagamento (simulação por prefixo de cartão)
   * 5. Cria matrícula
   * 6. Registra pagamento
   * 7. Registra auditoria
   *
   * @param {Object} params
   * @param {string} params.userName — nome do usuário
   * @param {string} params.email — email do usuário
   * @param {string} params.password — senha (opcional, default "123456" — compatibilidade com legado)
   * @param {number} params.courseId — ID do curso
   * @param {string} params.cardNumber — número do cartão de crédito
   * @returns {Object} { enrollmentId }
   */
  async execute({ userName, email, password, courseId, cardNumber }) {
    // Validação de campos obrigatórios
    const errors = this._validate({ userName, email, courseId, cardNumber });
    if (errors.length) {
      const err = new Error(errors[0]);
      err.statusCode = 400;
      throw err;
    }

    // Busca curso ativo
    const course = await this.courseModel.findById(courseId);
    if (!course) {
      const err = new Error('Curso não encontrado');
      err.statusCode = 404;
      throw err;
    }

    // Busca ou cria usuário
    let user = await this.userModel.findByEmail(email);
    if (!user) {
      const pwd = password || '123456'; // default legado
      const userId = await this.userModel.create(userName, email, pwd);
      user = { id: userId, name: userName, email };
    }

    // Processa pagamento (simulação)
    const paymentResult = this._processPayment(cardNumber);
    if (!paymentResult.approved) {
      const err = new Error('Pagamento recusado');
      err.statusCode = 400;
      throw err;
    }

    // Cria matrícula e pagamento
    const enrollmentId = await this.enrollmentModel.create(user.id, courseId);
    await this.paymentModel.create(enrollmentId, course.price, paymentResult.status);

    // Auditoria (não bloqueante — falha de auditoria não afeta resposta)
    try {
      await this.auditLogModel.create(`Checkout curso ${courseId} por ${user.id}`);
    } catch (auditErr) {
      console.error(`[AUDIT] Falha ao registrar auditoria: ${auditErr.message}`);
    }

    return { enrollment_id: enrollmentId };
  }

  /**
   * Valida campos obrigatórios do checkout.
   */
  _validate({ userName, email, courseId, cardNumber }) {
    const errors = [];
    if (!userName) errors.push('Nome do usuário é obrigatório');
    if (!email) errors.push('Email é obrigatório');
    if (!courseId) errors.push('ID do curso é obrigatório');
    if (!cardNumber) errors.push('Número do cartão é obrigatório');

    // Validação de formato de email
    if (email && !/^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$/.test(email)) {
      errors.push('Email inválido');
    }

    return errors;
  }

  /**
   * Simula processamento de pagamento.
   * Cartão iniciado com "4" (Visa) = aprovado, demais = recusado.
   * NÃO loga dados sensíveis do cartão.
   */
  _processPayment(cardNumber) {
    const approved = cardNumber.startsWith(VISA_CARD_PREFIX);
    return {
      approved,
      status: approved ? 'PAID' : 'DENIED',
    };
  }
}

module.exports = { CheckoutController };
