/**
 * Inicialização do banco de dados SQLite em memória.
 * Schema, seeds e conexão gerenciados aqui — sem God Class.
 * Senhas dos seeds são hasheadas (nunca plaintext).
 */
const sqlite3 = require('sqlite3').verbose();
const { hashPassword } = require('../utils/crypto');
const { PAYMENT_STATUS } = require('../utils/constants');

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

/**
 * Executa uma instrução SQL retornando uma Promise (sequencial).
 * @param {import('sqlite3').Database} db
 * @param {string} sql
 * @param {Array} [params]
 */
function run(db, sql, params = []) {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function (err) {
      if (err) return reject(err);
      resolve(this);
    });
  });
}

/**
 * Inicializa o banco: cria tabelas e insere seeds.
 * A senha do usuário seed é hasheada antes de persistir (nunca plaintext).
 * @returns {Promise<import('sqlite3').Database>}
 */
async function initDatabase() {
  const db = new sqlite3.Database(':memory:');

  for (const sql of SCHEMA_SQL) {
    await run(db, sql);
  }

  // Seed — senha forte (>= MIN_PASSWORD_LENGTH) hasheada via crypto.scrypt
  const leonanPassHash = await hashPassword('Leonan@123');
  await run(
    db,
    'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
    ['Leonan', 'leonan@fullcycle.com.br', leonanPassHash]
  );
  await run(
    db,
    'INSERT INTO courses (title, price, active) VALUES (?, ?, ?), (?, ?, ?)',
    ['Clean Architecture', 997.00, 1, 'Docker', 497.00, 1]
  );
  await run(
    db,
    'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
    [1, 1]
  );
  await run(
    db,
    'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
    [1, 997.00, PAYMENT_STATUS.PAID]
  );

  return db;
}

module.exports = { initDatabase };
