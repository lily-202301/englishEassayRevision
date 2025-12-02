import { Router } from 'express';
import {
  redeemBetaCode,
  getPointsBalance
} from '../controllers/pointsController.js';

const router = Router();

router.post('/redeem', redeemBetaCode);
router.get('/balance', getPointsBalance);

export default router;

