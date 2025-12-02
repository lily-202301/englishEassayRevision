import { DataTypes } from 'sequelize';
import sequelize from '../config/database.js';
import User from './User.js';

const EssayRecord = sequelize.define(
  'EssayRecord',
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
    original_text: {
      type: DataTypes.TEXT('medium'),
      allowNull: false
    },
    ai_feedback: {
      type: DataTypes.TEXT('medium'),
      allowNull: true
    },
    score: {
      type: DataTypes.DECIMAL(5, 2),
      allowNull: true
    },
    status: {
      type: DataTypes.ENUM('processing', 'completed'),
      allowNull: false,
      defaultValue: 'processing'
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
    tableName: 'essay_records',
    underscored: true,
    timestamps: true,
    createdAt: 'created_at',
    updatedAt: 'updated_at'
  }
);

User.hasMany(EssayRecord, { foreignKey: 'user_id' });
EssayRecord.belongsTo(User, { foreignKey: 'user_id' });

export default EssayRecord;

