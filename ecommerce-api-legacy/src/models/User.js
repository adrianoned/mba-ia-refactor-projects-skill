/**
 * User Model — acesso a dados da entidade Usuário.
 * Responsabilidades: CRUD, busca por email, hash de senha.
 */
const { hashPassword, verifyPassword } = require('../utils/crypto');

class UserModel {
  /**
   * @param {import('sqlite3').Database} db
   */
  constructor(db) {
    this.db = db;
  }

  findById(id) {
    return new Promise((resolve, reject) => {
      this.db.get('SELECT id, name, email, pass FROM users WHERE id = ?', [id], (err, row) => {
        if (err) return reject(err);
        resolve(row || null);
      });
    });
  }

  findByEmail(email) {
    return new Promise((resolve, reject) => {
      this.db.get('SELECT id, name, email, pass FROM users WHERE email = ?', [email], (err, row) => {
        if (err) return reject(err);
        resolve(row || null);
      });
    });
  }

  async create(name, email, password) {
    const passHash = await hashPassword(password);
    return new Promise((resolve, reject) => {
      this.db.run(
        'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
        [name, email, passHash],
        function (err) {
          if (err) return reject(err);
          resolve(this.lastID);
        }
      );
    });
  }

  deleteById(id) {
    return new Promise((resolve, reject) => {
      this.db.run('DELETE FROM users WHERE id = ?', [id], function (err) {
        if (err) return reject(err);
        resolve(this.changes);
      });
    });
  }

  /**
   * Busca múltiplos usuários por array de IDs.
   */
  findByIds(ids) {
    if (!ids.length) return Promise.resolve([]);
    const placeholders = ids.map(() => '?').join(',');
    return new Promise((resolve, reject) => {
      this.db.all(
        `SELECT id, name, email, pass FROM users WHERE id IN (${placeholders})`,
        ids,
        (err, rows) => {
          if (err) return reject(err);
          resolve(rows);
        }
      );
    });
  }

  /**
   * Serializa usuário para API (NUNCA inclui campo pass).
   */
  static toJSON(row) {
    if (!row) return null;
    return {
      id: row.id,
      name: row.name,
      email: row.email,
    };
  }
}

module.exports = { UserModel };
