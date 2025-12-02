import { DataTypes } from 'sequelize';
import sequelize from '../config/database.js';
import User from './User.js';

const PointsTransaction = sequelize.define(
  'PointsTransaction',
  {
    id: {
      type: DataTypes.BIGINT.UNSIGNED,
      autoIncrement: true,
      primaryKey: true
    },
    user_id: {
      type: DataTypes.BIGINT.UNSIGNED,
      allowNull: false
    },
    type: {
      type: DataTypes.ENUM(
        'topup',
        'spend',
        'redeem',
        'adjust',
        'system_adjust'
      ),
      allowNull: false
    },
    amount: {
      type: DataTypes.INTEGER,
      allowNull: false
    },
    description: {
      type: DataTypes.STRING(255),
      allowNull: true
    },
    created_at: {
      type: DataTypes.DATE,
      allowNull: false,
      defaultValue: DataTypes.NOW
    },
    updated_at: {
      type: DataTypes.DATE,
      allowNull: false,
      defaultValue: DataTypes.NOW
    }
  },
  {
    tableName: 'points_transactions',
    underscored: true,
    timestamps: true,
    createdAt: 'created_at',
    updatedAt: 'updated_at'
  }
);

User.hasMany(PointsTransaction, { foreignKey: 'user_id' });
PointsTransaction.belongsTo(User, { foreignKey: 'user_id' });

export default PointsTransaction;

