import { Sequelize } from 'sequelize';
import dotenv from 'dotenv';

dotenv.config();

const DIALECT = process.env.DB_DIALECT || 'mysql';

let sequelize;

if (DIALECT === 'sqlite') {
  sequelize = new Sequelize({
    dialect: 'sqlite',
    storage: process.env.SQLITE_STORAGE || ':memory:',
    logging: process.env.DB_LOGGING === 'true' ? console.log : false
  });
} else {
  sequelize = new Sequelize(
    process.env.DB_NAME || 'essay_app',
    process.env.DB_USER || 'root',
    process.env.DB_PASSWORD || '',
    {
      host: process.env.DB_HOST || '127.0.0.1',
      port: process.env.DB_PORT ? Number(process.env.DB_PORT) : 3306,
      dialect: 'mysql',
      logging: process.env.DB_LOGGING === 'true' ? console.log : false,
      timezone: '+08:00'
    }
  );
}

export default sequelize;

