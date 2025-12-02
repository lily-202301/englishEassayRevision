import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET || 'dev_secret';

// Bearer Token 认证中间件
export const authenticateToken = (req, res, next) => {
  try {
    const authHeader = req.headers['authorization'] || '';
    const token = authHeader.startsWith('Bearer ') ? authHeader.slice(7) : null;

    if (!token) {
      return res.status(401).json({ message: 'Unauthorized: missing token' });
    }

    const payload = jwt.verify(token, JWT_SECRET);
    // 与 authController.js 中 generateToken 的字段保持一致
    req.user = {
      id: payload.userId,
      phone: payload.phone
    };

    return next();
  } catch (err) {
    return res.status(401).json({ message: 'Unauthorized: invalid token' });
  }
};

export default authenticateToken;

