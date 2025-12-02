import { Router } from 'express';
import {
  submitEssay,
  getEssayHistory
} from '../controllers/essayController.js';

const router = Router();

router.post('/submit', submitEssay);
router.get('/history', getEssayHistory);

export default router;

