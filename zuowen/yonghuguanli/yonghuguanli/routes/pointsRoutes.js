import { Router } from 'express';
import {
  redeemBetaCode,
  getPointsBalance
} from '../controllers/pointsController.js';
import authenticateToken from '../middleware/authMiddleware.js';

const router = Router();

// 需要登录态，使用 Bearer token 注入 req.user.id
router.post('/redeem', authenticateToken, redeemBetaCode);
router.get('/balance', authenticateToken, getPointsBalance);

export default router;

