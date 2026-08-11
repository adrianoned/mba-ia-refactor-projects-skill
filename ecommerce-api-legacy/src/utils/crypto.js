/**
 * Funções seguras de hash de senha usando crypto.scrypt (nativo do Node.js).
 * Substitui a função badCrypto() caseira.
 */
const crypto = require('crypto');

const SALT_LENGTH = 16;
const KEY_LENGTH = 64;
const SCRYPT_OPTIONS = { N: 16384, r: 8, p: 1 };

/**
 * Gera hash seguro de senha com salt aleatório.
 * Formato de armazenamento: salt:derivedKey (ambos em hex)
 */
function hashPassword(password) {
  return new Promise((resolve, reject) => {
    const salt = crypto.randomBytes(SALT_LENGTH).toString('hex');
    crypto.scrypt(password, salt, KEY_LENGTH, SCRYPT_OPTIONS, (err, derivedKey) => {
      if (err) return reject(err);
      resolve(`${salt}:${derivedKey.toString('hex')}`);
    });
  });
}

/**
 * Verifica senha contra hash armazenado no formato salt:key.
 */
function verifyPassword(password, storedHash) {
  return new Promise((resolve, reject) => {
    const [salt, key] = storedHash.split(':');
    if (!salt || !key) return resolve(false);
    crypto.scrypt(password, salt, KEY_LENGTH, SCRYPT_OPTIONS, (err, derivedKey) => {
      if (err) return reject(err);
      resolve(key === derivedKey.toString('hex'));
    });
  });
}

module.exports = { hashPassword, verifyPassword };
