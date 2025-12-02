import express from 'express';
import dotenv from 'dotenv';
import authRoutes from './routes/authRoutes.js';
import pointsRoutes from './routes/pointsRoutes.js';
import essayRoutes from './routes/essayRoutes.js';
import adminRoutes from './routes/adminRoutes.js';
import sequelize from './config/database.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

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

    await sequelize.sync();
    console.log('Database synchronized');

    app.listen(PORT, () => {
      console.log(`Server is running on port ${PORT}`);
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
};

startServer();

