import express from 'express';
import dotenv from 'dotenv';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

import authRoutes from './routes/authRoutes.js';
import pointsRoutes from './routes/pointsRoutes.js';
import essayRoutes from './routes/essayRoutes.js';
import adminRoutes from './routes/adminRoutes.js';
import sequelize from './config/database.js';

dotenv.config();

// 计算 ESM 下的 __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

// 允许跨域（测试/未来前后端分离时需要）
app.use(cors({ origin: true }));

app.use(express.json());

// 确保上传临时目录存在（multer 用到）
const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir, { recursive: true });

// 静态托管测试页：访问 http://localhost:3000/test/
app.use('/test', express.static(path.join(__dirname, 'test-client')));

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.use('/api/auth', authRoutes);
app.use('/api/points', pointsRoutes);
app.use('/api/essay', essayRoutes);
app.use('/api/admin', adminRoutes);

const startServer = async () => {
  try {
    await sequelize.authenticate();
    console.log('Database connection established');

    // await sequelize.sync();
    await sequelize.sync({ alter: true });
    console.log('Database synchronized');

    app.listen(PORT, () => {
      console.log(`Server is running on port ${PORT}`);
      console.log(`Test page: http://localhost:${PORT}/test/`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
};

startServer();
