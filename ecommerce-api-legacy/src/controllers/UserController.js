/**
 * UserController — gerencia operações de usuário.
 */
class UserController {
  /**
   * @param {import('../models/User').UserModel} userModel
   */
  constructor(userModel) {
    this.userModel = userModel;
  }

  /**
   * Deleta um usuário por ID.
   * Nota: mantém o comportamento legado — deleta apenas o usuário,
   * matrículas e pagamentos permanecem (comportamento original preservado).
   *
   * @param {number} id
   * @returns {Object} resultado da operação
   */
  async delete(id) {
    const changes = await this.userModel.deleteById(id);
    if (changes === 0) {
      const err = new Error('Usuário não encontrado');
      err.statusCode = 404;
      throw err;
    }
    return { deleted: true, message: 'Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.' };
  }
}

module.exports = { UserController };
