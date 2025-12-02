import crypto from 'crypto';
import BetaCode from '../models/BetaCode.js';
import User from '../models/User.js';
import PointsTransaction from '../models/PointsTransaction.js';
import sequelize from '../config/database.js';

const MAX_GENERATE_COUNT = 200;
const DEFAULT_EXPIRE_DAYS = 30;

const buildCode = () => crypto.randomBytes(8).toString('hex');

export const generateBetaCodes = async (req, res) => {
  const count = Number(req.body.count);
  const points = Number(req.body.points);
  const expireDays = req.body.expireDays
    ? Number(req.body.expireDays)
    : DEFAULT_EXPIRE_DAYS;

  if (
    !Number.isInteger(count) ||
    count <= 0 ||
    count > MAX_GENERATE_COUNT ||
    !Number.isInteger(points) ||
    points <= 0
  ) {
    return res.status(400).json({
      message: `count must be 1-${MAX_GENERATE_COUNT}, points must be > 0`
    });
  }

  const expireAt = new Date();
  expireAt.setDate(expireAt.getDate() + expireDays);

  try {
    const codes = [];
    const seen = new Set();

    while (codes.length < count) {
      const code = buildCode();
      if (seen.has(code)) continue;
      seen.add(code);
      codes.push({
        code,
        points_value: points,
        expire_at: expireAt
      });
    }

    await BetaCode.bulkCreate(codes, { validate: true });

    return res.status(201).json({
      message: 'Codes generated',
      count: codes.length,
      expire_at: expireAt,
      codes: codes.map((item) => item.code)
    });
  } catch (error) {
    console.error('Generate codes failed:', error);
    return res.status(500).json({ message: 'Internal server error' });
  }
};

export const adjustUserPoints = async (req, res) => {
  const { phone, amount, reason } = req.body;
  const adjustment = Number(amount);

  if (!phone || !Number.isFinite(adjustment) || adjustment === 0) {
    return res
      .status(400)
      .json({ message: 'phone and non-zero numeric amount are required' });
  }

  const transaction = await sequelize.transaction();

  try {
    const user = await User.findOne({
      where: { phone },
      transaction,
      lock: transaction.LOCK.UPDATE
    });

    if (!user) {
      await transaction.rollback();
      return res.status(404).json({ message: 'User not found' });
    }

    const newBalance = user.points_balance + adjustment;

    await user.update({ points_balance: newBalance }, { transaction });

    await PointsTransaction.create(
      {
        user_id: user.id,
        type: 'system_adjust',
        amount: adjustment,
        description: reason || 'SYSTEM_ADJUST'
      },
      { transaction }
    );

    await transaction.commit();

    return res.json({
      message: 'Points adjusted',
      balance: newBalance
    });
  } catch (error) {
    await transaction.rollback();
    console.error('Adjust points failed:', error);
    return res.status(500).json({ message: 'Internal server error' });
  }
};

