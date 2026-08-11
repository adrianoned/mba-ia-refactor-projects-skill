/**
 * ReportController — gera relatório financeiro agregado por curso.
 * Substitui as queries N+1 por queries batch (4 queries no total).
 */
class ReportController {
  /**
   * @param {import('../models/Course').CourseModel} courseModel
   * @param {import('../models/Enrollment').EnrollmentModel} enrollmentModel
   * @param {import('../models/Payment').PaymentModel} paymentModel
   * @param {import('../models/User').UserModel} userModel
   */
  constructor(courseModel, enrollmentModel, paymentModel, userModel) {
    this.courseModel = courseModel;
    this.enrollmentModel = enrollmentModel;
    this.paymentModel = paymentModel;
    this.userModel = userModel;
  }

  /**
   * Gera relatório financeiro completo.
   * Estratégia: 4 queries batch em vez de N+1 queries.
   *
   * @returns {Array} Relatório por curso com receita e lista de alunos
   */
  async generate() {
    // Query 1: todos os cursos
    const courses = await this.courseModel.findAll();
    if (!courses.length) return [];

    const courseIds = courses.map(c => c.id);

    // Query 2: todas as matrículas para todos os cursos de uma vez
    const enrollments = await this.enrollmentModel.findByCourseIds(courseIds);
    if (!enrollments.length) {
      return courses.map(c => ({
        course: c.title,
        revenue: 0,
        students: [],
      }));
    }

    // Coleta IDs para queries batch
    const userIds = [...new Set(enrollments.map(e => e.user_id))];
    const enrollmentIds = enrollments.map(e => e.id);

    // Query 3: todos os usuários de uma vez
    const users = await this.userModel.findByIds(userIds);
    const userMap = {};
    users.forEach(u => { userMap[u.id] = u; });

    // Query 4: todos os pagamentos de uma vez
    const payments = await this.paymentModel.findByEnrollmentIds(enrollmentIds);
    const paymentByEnrollment = {};
    payments.forEach(p => { paymentByEnrollment[p.enrollment_id] = p; });

    // Agrupa matrículas por curso
    const enrollmentsByCourse = {};
    enrollments.forEach(enr => {
      if (!enrollmentsByCourse[enr.course_id]) {
        enrollmentsByCourse[enr.course_id] = [];
      }
      enrollmentsByCourse[enr.course_id].push(enr);
    });

    // Monta relatório em memória — sem queries adicionais
    return courses.map(c => {
      const courseEnrollments = enrollmentsByCourse[c.id] || [];
      let revenue = 0;
      const students = courseEnrollments.map(enr => {
        const payment = paymentByEnrollment[enr.id];
        const user = userMap[enr.user_id];
        const amount = (payment && payment.status === 'PAID') ? payment.amount : 0;
        revenue += amount;
        return {
          student: user ? user.name : 'Unknown',
          paid: amount,
        };
      });

      return {
        course: c.title,
        revenue,
        students,
      };
    });
  }
}

module.exports = { ReportController };
