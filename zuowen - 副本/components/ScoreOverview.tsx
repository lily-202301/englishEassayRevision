import React from 'react';
import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { OverallEvaluation } from '../types';

interface Props {
  evaluation: OverallEvaluation;
}

const ScoreOverview: React.FC<Props> = ({ evaluation }) => {
  const data = [
    { subject: '切题度', A: 90, fullMark: 100 },
    { subject: '词汇语法', A: 50, fullMark: 100 },
    { subject: '逻辑结构', A: 80, fullMark: 100 },
    { subject: '内容详情', A: 70, fullMark: 100 },
  ];

  const labelMap: {[key: string]: string} = {
    relevance: '切题度',
    grammar_vocab: '词汇语法',
    logic_structure: '逻辑结构',
    content: '内容详情'
  };

  const [current, total] = evaluation.total_score.split('/').map(Number);

  return (
    <div className="flex flex-col gap-6">
        {/* Top Card: Score & Badge */}
        <div className="bg-gradient-to-br from-stone-50 to-white rounded-2xl p-6 border border-stone-100 shadow-sm relative overflow-hidden">
             {/* Decorative Elements */}
             <div className="absolute right-0 top-0 w-32 h-32 bg-stone-100 rounded-bl-[100px] -mr-8 -mt-8 opacity-50"></div>
             
             <div className="flex justify-between items-start relative z-10">
                 <div>
                     <h3 className="text-xs font-bold text-stone-400 uppercase tracking-widest mb-1">Total Score</h3>
                     <div className="flex items-baseline gap-1">
                         <span className="text-5xl font-serif font-bold text-stone-800">{current}</span>
                         <span className="text-lg text-stone-400">/{total}</span>
                     </div>
                 </div>
                 <div className="bg-stone-900 text-white px-4 py-1.5 rounded-full text-sm font-bold shadow-lg">
                    {evaluation.tier}
                 </div>
             </div>

             <div className="mt-6 pt-6 border-t border-stone-100">
                <div className="grid grid-cols-4 gap-2">
                     {Object.entries(evaluation.score_breakdown).map(([key, value]) => (
                        <div key={key} className="text-center">
                            <div className="w-full bg-stone-100 rounded-full h-1.5 mb-2 overflow-hidden">
                                <div className="h-full bg-stone-800" style={{ width: '70%' }}></div> {/* Mock progress */}
                            </div>
                            <div className="text-[10px] text-stone-500 font-medium">{labelMap[key]}</div>
                        </div>
                     ))}
                </div>
             </div>
        </div>

        {/* Middle: Radar Chart (Centered) */}
        <div className="h-48 w-full -my-2">
            <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="65%" data={data}>
              <PolarGrid stroke="#e5e7eb" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: '#9ca3af', fontSize: 10, fontWeight: 600 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
              <Radar
                name="Score"
                dataKey="A"
                stroke="#2d3748"
                strokeWidth={2}
                fill="#cbd5e1"
                fillOpacity={0.4}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        {/* Bottom: Text Evaluation */}
        <div className="bg-stone-50 rounded-xl p-5 border border-stone-100/50">
             <h3 className="text-sm font-bold text-stone-900 mb-3 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-stone-900"></span>
                总评与建议
             </h3>
             <p className="text-sm text-stone-600 leading-relaxed font-serif text-justify">
                {evaluation.brief_comment}
             </p>
        </div>
    </div>
  );
};

export default ScoreOverview;