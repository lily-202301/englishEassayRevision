import sequelize from '../config/database.js';
import User from '../models/User.js';
import PointsTransaction from '../models/PointsTransaction.js';
import EssayRecord from '../models/EssayRecord.js';

const DEDUCTION_PER_SUBMISSION = 10;

const resolveUserId = (req) =>
  req.user?.id ||
  req.body.userId ||
  req.query.userId ||
  req.headers['x-user-id'];

export const submitEssay = async (req, res) => {
  const { content } = req.body;
  const userId = resolveUserId(req);

  if (!content || !userId) {
    return res.status(400).json({ message: 'content and userId are required' });
  }

  try {
    const user = await User.findByPk(userId);

    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    if (user.points_balance < DEDUCTION_PER_SUBMISSION) {
      return res.status(400).json({ message: 'Insufficient points' });
    }

    const transaction = await sequelize.transaction();

    try {
      const newBalance = user.points_balance - DEDUCTION_PER_SUBMISSION;

      // 每次提交作文默认扣除 10 积分，可根据业务配置调整。
      await user.update(
        { points_balance: newBalance },
        { transaction }
      );

      await PointsTransaction.create(
        {
          user_id: userId,
          type: 'spend',
          amount: -DEDUCTION_PER_SUBMISSION,
          description: 'Essay submission deduction'
        },
        { transaction }
      );

      const record = await EssayRecord.create(
        {
          user_id: userId,
          original_text: content,
          status: 'processing'
        },
        { transaction }
      );

      await transaction.commit();

      return res.status(201).json({
        message: 'Essay submitted',
        record: {
          id: record.id,
          status: record.status,
          created_at: record.created_at
        },
        balance: newBalance
      });
    } catch (err) {
      await transaction.rollback();
      throw err;
    }
  } catch (error) {
    console.error('Submit essay failed:', error);
    return res.status(500).json({ message: 'Internal server error' });
  }
};

export const getEssayHistory = async (req, res) => {
  const userId = resolveUserId(req);

  if (!userId) {
    return res.status(400).json({ message: 'userId is required' });
  }

  try {
    const records = await EssayRecord.findAll({
      where: { user_id: userId },
      order: [['created_at', 'DESC']]
    });

    return res.json({ records });
  } catch (error) {
    console.error('Fetch essay history failed:', error);
    return res.status(500).json({ message: 'Internal server error' });
  }
};

