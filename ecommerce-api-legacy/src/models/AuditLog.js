/**
 * AuditLog Model — acesso a dados da entidade Log de Auditoria.
 */
class AuditLogModel {
  /**
   * @param {import('sqlite3').Database} db
   */
  constructor(db) {
    this.db = db;
  }

  create(action) {
    return new Promise((resolve, reject) => {
      this.db.run(
        "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
        [action],
        function (err) {
          if (err) return reject(err);
          resolve(this.lastID);
        }
      );
    });
  }

  static toJSON(row) {
    if (!row) return null;
    return {
      id: row.id,
      action: row.action,
      createdAt: row.created_at,
    };
  }
}

module.exports = { AuditLogModel };
