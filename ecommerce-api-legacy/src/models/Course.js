/**
 * Course Model — acesso a dados da entidade Curso.
 */
class CourseModel {
  /**
   * @param {import('sqlite3').Database} db
   */
  constructor(db) {
    this.db = db;
  }

  findById(id) {
    return new Promise((resolve, reject) => {
      this.db.get(
        'SELECT id, title, price, active FROM courses WHERE id = ? AND active = 1',
        [id],
        (err, row) => {
          if (err) return reject(err);
          resolve(row || null);
        }
      );
    });
  }

  findAll() {
    return new Promise((resolve, reject) => {
      this.db.all('SELECT id, title, price, active FROM courses', [], (err, rows) => {
        if (err) return reject(err);
        resolve(rows);
      });
    });
  }

  /**
   * Serializa curso para API.
   */
  static toJSON(row) {
    if (!row) return null;
    return {
      id: row.id,
      title: row.title,
      price: row.price,
      active: !!row.active,
    };
  }
}

module.exports = { CourseModel };
