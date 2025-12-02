/* eslint-disable no-console */
process.env.DB_DIALECT = 'sqlite';
process.env.SQLITE_STORAGE = ':memory:';
process.env.JWT_SECRET = process.env.JWT_SECRET || 'test_secret';
process.env.JWT_EXPIRES_IN = '1d';

const { default: sequelize } = await import('../config/database.js');
const { default: User } = await import('../models/User.js');
const { default: BetaCode } = await import('../models/BetaCode.js');
const { login } = await import('../controllers/authController.js');
const {
  redeemBetaCode,
  getPointsBalance
} = await import('../controllers/pointsController.js');
const {
  submitEssay,
  getEssayHistory
} = await import('../controllers/essayController.js');
const {
  generateBetaCodes,
  adjustUserPoints
} = await import('../controllers/adminController.js');

const mockRes = () => {
  const res = {
    statusCode: 200,
    body: null
  };
  res.status = (code) => {
    res.statusCode = code;
    return res;
  };
  res.json = (payload) => {
    res.body = payload;
    return res;
  };
  return res;
};

const invoke = async (handler, { body = {}, query = {}, headers = {} } = {}) => {
  const req = { body, query, headers };
  const res = mockRes();
  await handler(req, res);
  if (res.statusCode >= 400) {
    throw new Error(
      `Handler ${handler.name} failed: status=${res.statusCode}, body=${JSON.stringify(
        res.body
      )}`
    );
  }
  return res.body;
};

try {
  await sequelize.sync({ force: true });
  console.log('SQLite in-memory DB ready.');

  const loginResult = await invoke(login, {
    body: { phone: '13800000000', code: '1234', openid: 'wx_test' }
  });
  console.log('Login result:', loginResult);
  const userId = loginResult.user.id;

  const codeResponse = await invoke(generateBetaCodes, {
    body: { count: 1, points: 50, expireDays: 7 }
  });
  const betaCode = codeResponse.codes[0];
  console.log('Generated beta code:', betaCode);

  await invoke(redeemBetaCode, {
    body: { code: betaCode, userId }
  });
  console.log('Redeem success');

  const balanceAfterRedeem = await invoke(getPointsBalance, {
    query: { userId }
  });
  console.log('Balance after redeem:', balanceAfterRedeem);

  await invoke(submitEssay, {
    body: { content: 'This is a test essay', userId }
  });
  console.log('Essay submission success');

  const history = await invoke(getEssayHistory, {
    query: { userId }
  });
  console.log('Essay history count:', history.records.length);

  await invoke(adjustUserPoints, {
    body: { phone: '13800000000', amount: 20, reason: 'manual adjust' }
  });
  console.log('Admin adjust success');

  const finalBalance = await invoke(getPointsBalance, {
    query: { userId }
  });
  console.log('Final balance:', finalBalance);

  console.log('Smoke test completed successfully 🎉');
  process.exit(0);
} catch (error) {
  console.error('Smoke test failed:', error);
  process.exit(1);
}

