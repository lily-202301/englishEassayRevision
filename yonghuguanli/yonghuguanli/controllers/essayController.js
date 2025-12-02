import sequelize from '../config/database.js';
import User from '../models/User.js';
import PointsTransaction from '../models/PointsTransaction.js';
import EssayRecord from '../models/EssayRecord.js';
import axios from 'axios';
import FormData from 'form-data';
import fs from 'fs';

const DEDUCTION_PER_SUBMISSION = 10;
const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://127.0.0.1:8000'; // Python微服务地址

const resolveUserId = (req) => req.user?.id || req.body.userId || req.query.userId || req.headers['x-user-id'];

// 提交作文的新逻辑
export const submitEssay = async (req, res) => {
  const userId = resolveUserId(req);

  if (!req.files || req.files.length === 0) {
    return res.status(400).json({ message: 'No image files uploaded.' });
  }
  if (!userId) {
    return res.status(400).json({ message: 'userId is required' });
  }

  let record;

  try {
    const user = await User.findByPk(userId);
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }
    if (user.points_balance < DEDUCTION_PER_SUBMISSION) {
      return res.status(400).json({ message: 'Insufficient points' });
    }

    // 1. 先在数据库中创建记录并扣除积分
    const transaction = await sequelize.transaction();
    try {
      const newBalance = user.points_balance - DEDUCTION_PER_SUBMISSION;
      await user.update({ points_balance: newBalance }, { transaction });
      await PointsTransaction.create({
          user_id: userId,
          type: 'spend',
          amount: -DEDUCTION_PER_SUBMISSION,
          description: 'Essay submission deduction'
      }, { transaction });

      record = await EssayRecord.create({
          user_id: userId,
        original_text: `Processing ${req.files.length} image(s)...`,
          status: 'processing'
      }, { transaction });

      await transaction.commit();
    } catch (err) {
      await transaction.rollback();
      throw err;
    }

    // 2. 异步调用 Python 微服务
    const formData = new FormData();
    req.files.forEach(file => {
      formData.append('images', fs.createReadStream(file.path), file.originalname);
    });

    const cleanup = () => {
      try { req.files.forEach(file => fs.existsSync(file.path) && fs.unlinkSync(file.path)); } catch {}
    };

    axios.post(`${PYTHON_API_URL}/grade_essay`, formData, {
      headers: formData.getHeaders()
    }).then(async response => {
      const { task_id } = response.data;
      await record.update({ celery_task_id: task_id });
      console.log(`[EssaySubmit] Record ${record.id} linked to Celery task ${task_id}`);
      cleanup();
    }).catch(async err => {
      console.error(`[EssaySubmit] Failed to call Python service for record ${record.id}:`, err.message);
      await record.update({ status: 'failed', ai_feedback: JSON.stringify({ error: 'Failed to start processing.' }) });
      cleanup();
    });

    // 4. 立即返回响应给用户（按前端规范封装 data）
    return res.status(202).json({
      code: 0,
      msg: 'ok',
      data: {
        recordId: record.id
      }
    });

  } catch (error) {
    console.error('Submit essay failed:', error);
    if (record) {
      try { await record.update({ status: 'failed', ai_feedback: JSON.stringify({ error: 'Internal server error during submission.' }) }); } catch {}
    }
    return res.status(500).json({ code: 500, msg: 'Internal server error' });
  }
};

// 新增：查询批改结果的接口
export const getEssayResult = async (req, res) => {
  const { id } = req.params;
  const userId = resolveUserId(req);

  try {
    const record = await EssayRecord.findByPk(id);
    if (!record) {
      return res.status(404).json({ message: 'Record not found' });
    }
    // 安全检查：确保用户只能查询自己的记录
    if (record.user_id !== parseInt(userId, 10)) {
        return res.status(403).json({ message: 'Forbidden' });
    }

    // 如果任务已完成，直接返回存储的结果
    if (record.status === 'completed' || record.status === 'failed') {
      return res.json({ 
        id: record.id, 
        status: record.status, 
        result: record.ai_feedback ? JSON.parse(record.ai_feedback) : null 
      });
    }

    // 如果任务还在处理中，去查询 Python 微服务
    if (record.celery_task_id) {
      const response = await axios.get(`${PYTHON_API_URL}/result/${record.celery_task_id}`);
      const { status, result } = response.data;

      // 如果 Python 端任务已完成
      if (status === 'SUCCESS') {
        // 将最终结果存入我们的数据库，并更新状态
        await record.update({ status: 'completed', ai_feedback: JSON.stringify(result) });
        return res.json({ id: record.id, status: 'completed', result });
      } else if (status === 'FAILURE') {
        await record.update({ status: 'failed', ai_feedback: JSON.stringify(result) });
        return res.json({ id: record.id, status: 'failed', result });
      } else {
        // 任务仍在进行中
        return res.json({ id: record.id, status: 'processing', result: null });
      }
    } else {
      // celery_task_id 还未被更新，说明仍在排队或调用失败
      return res.json({ id: record.id, status: 'processing', result: null });
    }

  } catch (error) {
    console.error(`Fetch essay result for record ${id} failed:`, error.message);
    return res.status(500).json({ message: 'Internal server error' });
  }
};

// 获取历史记录的逻辑保持不变
export const getEssayHistory = async (req, res) => {
  const userId = resolveUserId(req);
  if (!userId) {
    return res.status(400).json({ message: 'userId is required' });
  }
  try {
    const records = await EssayRecord.findAll({
      where: { user_id: userId },
      order: [['created_at', 'DESC']],
      attributes: ['id', 'status', 'created_at'] // 优化返回字段，不返回大文本
    });
    return res.json({ records });
  } catch (error) {
    console.error('Fetch essay history failed:', error);
    return res.status(500).json({ message: 'Internal server error' });
  }
};
