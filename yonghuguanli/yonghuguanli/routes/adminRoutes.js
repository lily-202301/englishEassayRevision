import { Router } from 'express';
import {
  generateBetaCodes,
  adjustUserPoints
} from '../controllers/adminController.js';

const router = Router();

router.post('/generate-codes', generateBetaCodes);
router.post('/users/adjust-points', adjustUserPoints);

export default router;

