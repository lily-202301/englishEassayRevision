import jwt from 'jsonwebtoken';
import User from '../models/User.js';

const TOKEN_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '7d';
const JWT_SECRET = process.env.JWT_SECRET || 'dev_secret';

const generateToken = (user) =>
  jwt.sign(
    {
      userId: user.id,
      phone: user.phone
    },
    JWT_SECRET,
    { expiresIn: TOKEN_EXPIRES_IN }
  );

export const login = async (req, res) => {
  const { phone, code, openid } = req.body;

  if (!phone || !code || !openid) {
    return res.status(400).json({
      message: 'phone, code, openid are required'
    });
  }

  try {
    const now = new Date();
    let user = await User.findOne({ where: { phone } });

    if (!user) {
      user = await User.create({
        phone,
        openid,
        last_login_at: now
      });
    } else {
      await user.update({
        openid,
        last_login_at: now
      });
    }

    const token = generateToken(user);

    return res.json({
      token,
      user: {
        id: user.id,
        phone: user.phone,
        openid: user.openid,
        points_balance: user.points_balance,
        last_login_at: user.last_login_at
      }
    });
  } catch (error) {
    console.error('Login failed:', error);
    return res.status(500).json({ message: 'Internal server error' });
  }
};

