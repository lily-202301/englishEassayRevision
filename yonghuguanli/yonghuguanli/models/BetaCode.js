import { DataTypes } from 'sequelize';
import sequelize from '../config/database.js';
import User from './User.js';

const BetaCode = sequelize.define(
  'BetaCode',
  {
    code: {
      type: DataTypes.STRING(64),
      primaryKey: true
    },
    points_value: {
      type: DataTypes.INTEGER,
      allowNull: false
    },
    is_used: {
      type: DataTypes.BOOLEAN,
      allowNull: false,
      defaultValue: false
    },
    used_by_user_id: {
      type: DataTypes.BIGINT.UNSIGNED,
      allowNull: true
    },
    expire_at: {
      type: DataTypes.DATE,
      allowNull: false
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
    tableName: 'beta_codes',
    underscored: true,
    timestamps: true,
    createdAt: 'created_at',
    updatedAt: 'updated_at'
  }
);

BetaCode.belongsTo(User, { foreignKey: 'used_by_user_id', as: 'usedBy' });

export default BetaCode;

