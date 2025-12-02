import { Router } from 'express';
import multer from 'multer';
import { submitEssay, getEssayHistory, getEssayResult } from '../controllers/essayController.js';
import { authenticateToken } from '../middleware/authMiddleware.js'; // 假设认证中间件存在

const router = Router();

// 配置 multer 用于处理文件上传
// 我们将文件保存在临时目录中，处理后由 controller 删除
const upload = multer({ dest: 'uploads/' });

// 提交作文的路由，使用 multer 中间件处理最多5张图片，并添加token认证
router.post('/submit', authenticateToken, upload.array('images', 5), submitEssay);

// 获取历史记录的路由，添加token认证
router.get('/history', authenticateToken, getEssayHistory);

// 新增：获取单个作文批改结果的路由，添加token认证
router.get('/result/:id', authenticateToken, getEssayResult);

export default router;
