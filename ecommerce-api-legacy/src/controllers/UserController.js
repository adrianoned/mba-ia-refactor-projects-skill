/**
 * UserController — gerencia operações de usuário.
 * A deleção remove também matrículas e pagamentos vinculados (sem órfãos).
 */
class UserController {
  /**
   * @param {import('../models/User').UserModel} userModel
   * @param {import('../models/Enrollment').EnrollmentModel} enrollmentModel
   * @param {import('../models/Payment').PaymentModel} paymentModel
   */
  constructor(userModel, enrollmentModel, paymentModel) {
    this.userModel = userModel;
    this.enrollmentModel = enrollmentModel;
    this.paymentModel = paymentModel;
  }

  /**
   * Deleta um usuário por ID, removendo primeiro matrículas e pagamentos
   * vinculados para não deixar registros órfãos no banco.
   *
   * @param {number} id
   * @returns {Object} resultado da operação
   */
  async delete(id) {
    if (!Number.isInteger(id) || id <= 0) {
      const err = new Error('ID inválido');
      err.statusCode = 400;
      throw err;
    }

    const user = await this.userModel.findById(id);
    if (!user) {
      const err = new Error('Usuário não encontrado');
      err.statusCode = 404;
      throw err;
    }

    const enrollments = await this.enrollmentModel.findByUserId(id);
    if (enrollments.length) {
      await this.paymentModel.deleteByEnrollmentIds(enrollments.map(e => e.id));
      await this.enrollmentModel.deleteByUserId(id);
    }

    await this.userModel.deleteById(id);

    return { deleted: true, message: 'Usuário deletado' };
  }
}

module.exports = { UserController };
