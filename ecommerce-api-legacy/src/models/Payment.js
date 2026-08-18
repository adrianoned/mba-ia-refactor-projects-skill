/**
 * Payment Model — acesso a dados da entidade Pagamento.
 */
class PaymentModel {
  /**
   * @param {import('sqlite3').Database} db
   */
  constructor(db) {
    this.db = db;
  }

  create(enrollmentId, amount, status) {
    return new Promise((resolve, reject) => {
      this.db.run(
        'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
        [enrollmentId, amount, status],
        function (err) {
          if (err) return reject(err);
          resolve(this.lastID);
        }
      );
    });
  }

  findByEnrollmentId(enrollmentId) {
    return new Promise((resolve, reject) => {
      this.db.get(
        'SELECT id, enrollment_id, amount, status FROM payments WHERE enrollment_id = ?',
        [enrollmentId],
        (err, row) => {
          if (err) return reject(err);
          resolve(row || null);
        }
      );
    });
  }

  /**
   * Busca pagamentos para múltiplas matrículas de uma vez (evita N+1).
   */
  findByEnrollmentIds(enrollmentIds) {
    if (!enrollmentIds.length) return Promise.resolve([]);
    const placeholders = enrollmentIds.map(() => '?').join(',');
    return new Promise((resolve, reject) => {
      this.db.all(
        `SELECT id, enrollment_id, amount, status FROM payments WHERE enrollment_id IN (${placeholders})`,
        enrollmentIds,
        (err, rows) => {
          if (err) return reject(err);
          resolve(rows);
        }
      );
    });
  }

  /**
   * Remove pagamentos de múltiplas matrículas de uma vez (cascata na deleção).
   */
  deleteByEnrollmentIds(enrollmentIds) {
    if (!enrollmentIds.length) return Promise.resolve(0);
    const placeholders = enrollmentIds.map(() => '?').join(',');
    return new Promise((resolve, reject) => {
      this.db.run(
        `DELETE FROM payments WHERE enrollment_id IN (${placeholders})`,
        enrollmentIds,
        function (err) {
          if (err) return reject(err);
          resolve(this.changes);
        }
      );
    });
  }

  static toJSON(row) {
    if (!row) return null;
    return {
      id: row.id,
      enrollmentId: row.enrollment_id,
      amount: row.amount,
      status: row.status,
    };
  }
}

module.exports = { PaymentModel };
