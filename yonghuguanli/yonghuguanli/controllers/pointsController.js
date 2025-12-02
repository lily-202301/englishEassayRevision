import sequelize from '../config/database.js';
import User from '../models/User.js';
import BetaCode from '../models/BetaCode.js';
import PointsTransaction from '../models/PointsTransaction.js';

const resolveUserId = (req) =>
  req.user?.id ||
  req.body.userId ||
  req.query.userId ||
  req.headers['x-user-id'];

export const redeemBetaCode = async (req, res) => {
  const { code } = req.body;
  const userId = resolveUserId(req);

  if (!code || !userId) {
    return res.status(400).json({ message: 'code and userId are required' });
  }

  const transaction = await sequelize.transaction();

  try {
    const user = await User.findByPk(userId, {
      transaction,
      lock: transaction.LOCK.UPDATE
    });

    if (!user) {
      await transaction.rollback();
      return res.status(404).json({ message: 'User not found' });
    }

    const betaCode = await BetaCode.findOne({
      where: { code },
      transaction,
      lock: transaction.LOCK.UPDATE
    });

    if (!betaCode) {
      await transaction.rollback();
      return res.status(404).json({ message: 'Invalid code' });
    }

    const now = new Date();

    if (betaCode.is_used) {
      await transaction.rollback();
      return res.status(400).json({ message: 'Code already used' });
    }

    if (betaCode.expire_at && new Date(betaCode.expire_at) < now) {
      await transaction.rollback();
      return res.status(400).json({ message: 'Code expired' });
    }

    await betaCode.update(
      {
        is_used: true,
        used_by_user_id: userId
      },
      { transaction }
    );

    const pointsDelta = betaCode.points_value;
    const newBalance = user.points_balance + pointsDelta;

    await user.update(
      { points_balance: newBalance },
      { transaction }
    );

    await PointsTransaction.create(
      {
        user_id: userId,
        type: 'redeem',
        amount: pointsDelta,
        description: `Redeemed beta code ${betaCode.code}`
      },
      { transaction }
    );

    await transaction.commit();

    return res.json({
      message: 'Redeem success',
      points_added: pointsDelta,
      balance: newBalance
    });
  } catch (error) {
    await transaction.rollback();
    console.error('Redeem failed:', error);
    return res.status(500).json({ message: 'Internal server error' });
  }
};

export const getPointsBalance = async (req, res) => {
  const userId = resolveUserId(req);

  if (!userId) {
    return res.status(400).json({ message: 'userId is required' });
  }

  try {
    const user = await User.findByPk(userId);

    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    return res.json({
      balance: user.points_balance
    });
  } catch (error) {
    console.error('Fetch balance failed:', error);
    return res.status(500).json({ message: 'Internal server error' });
  }
};

