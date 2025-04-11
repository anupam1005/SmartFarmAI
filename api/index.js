const express = require('express');
const pool = require('../db/connect');

const app = express();
app.use(express.json());

app.get('/', (req, res) => {
  res.send('SmartFarmAI API is running!');
});

app.get('/users', async (req, res) => {
  const result = await pool.query('SELECT * FROM users');
  res.json(result.rows);
});

module.exports = app;
