/**
 * Enrollment Model — acesso a dados da entidade Matrícula.
 */
class EnrollmentModel {
  /**
   * @param {import('sqlite3').Database} db
   */
  constructor(db) {
    this.db = db;
  }

  create(userId, courseId) {
    return new Promise((resolve, reject) => {
      this.db.run(
        'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
        [userId, courseId],
        function (err) {
          if (err) return reject(err);
          resolve(this.lastID);
        }
      );
    });
  }

  findByCourseId(courseId) {
    return new Promise((resolve, reject) => {
      this.db.all(
        'SELECT id, user_id, course_id FROM enrollments WHERE course_id = ?',
        [courseId],
        (err, rows) => {
          if (err) return reject(err);
          resolve(rows);
        }
      );
    });
  }

  /**
   * Busca matrículas para múltiplos cursos de uma vez (evita N+1).
   */
  findByCourseIds(courseIds) {
    if (!courseIds.length) return Promise.resolve([]);
    const placeholders = courseIds.map(() => '?').join(',');
    return new Promise((resolve, reject) => {
      this.db.all(
        `SELECT id, user_id, course_id FROM enrollments WHERE course_id IN (${placeholders})`,
        courseIds,
        (err, rows) => {
          if (err) return reject(err);
          resolve(rows);
        }
      );
    });
  }

  static toJSON(row) {
    if (!row) return null;
    return {
      id: row.id,
      userId: row.user_id,
      courseId: row.course_id,
    };
  }
}

module.exports = { EnrollmentModel };
