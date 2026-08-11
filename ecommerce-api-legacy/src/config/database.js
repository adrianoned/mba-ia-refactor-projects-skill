/**
 * Inicialização do banco de dados SQLite em memória.
 * Schema, seeds e conexão gerenciados aqui — sem God Class.
 */
const sqlite3 = require('sqlite3').verbose();

const SCHEMA_SQL = [
  `CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    pass TEXT NOT NULL
  )`,
  `CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    price REAL NOT NULL,
    active INTEGER NOT NULL DEFAULT 1
  )`,
  `CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (course_id) REFERENCES courses(id)
  )`,
  `CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (enrollment_id) REFERENCES enrollments(id)
  )`,
  `CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    created_at DATETIME DEFAULT (datetime('now'))
  )`,
];

const SEED_SQL = [
  `INSERT INTO users (name, email, pass) VALUES ('Leonan', 'leonan@fullcycle.com.br', '123')`,
  `INSERT INTO courses (title, price, active) VALUES ('Clean Architecture', 997.00, 1), ('Docker', 497.00, 1)`,
  `INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)`,
  `INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, 'PAID')`,
];

/**
 * Inicializa o banco: cria tabelas e insere seeds.
 * Retorna a instância do banco.
 */
function initDatabase() {
  const db = new sqlite3.Database(':memory:');

  db.serialize(() => {
    SCHEMA_SQL.forEach(sql => db.run(sql));
    SEED_SQL.forEach(sql => db.run(sql));
  });

  return db;
}

module.exports = { initDatabase };
