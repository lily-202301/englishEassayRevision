import React from 'react';
import { EssayData, HighlightPoint, ImprovementPoint } from '../types';
import { ThumbsUp, ArrowUpCircle, Bookmark, Star } from 'lucide-react';

interface Props {
  data: EssayData;
}

const AnalysisSection: React.FC<Props> = ({ data }) => {
  return (
    <div className="space-y-6">
        {/* Highlights */}
        <div className="bg-white rounded-xl shadow-sm border border-stone-100 p-5 relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-16 h-16 bg-green-50 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110"></div>
            
            <div className="flex items-center gap-2 mb-4 relative z-10">
                <ThumbsUp size={16} className="text-green-600" />
                <h3 className="font-bold text-gray-900 text-sm">Highlights</h3>
            </div>

            <div className="space-y-5 relative z-10">
                {Object.entries(data.highlights).map(([category, points]) => (
                    <div key={category}>
                        <h4 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2">{category}</h4>
                        <ul className="space-y-3">
                            {(points as HighlightPoint[]).map((p, i) => (
                                <li key={i}>
                                    <div className="flex gap-2.5">
                                        <Star size={12} className="text-yellow-400 shrink-0 mt-1 fill-yellow-400" />
                                        <div>
                                            <p className="font-bold text-gray-800 text-xs mb-1">{p.point}</p>
                                            <div className="text-xs text-gray-500 font-serif italic pl-2 border-l-2 border-stone-100">
                                                "{p.evidence}"
                                            </div>
                                        </div>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    </div>
                ))}
            </div>
        </div>

        {/* Improvements */}
        <div className="bg-white rounded-xl shadow-sm border border-stone-100 p-5 relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-16 h-16 bg-blue-50 rounded-bl-full -mr-4 -mt-4 transition-transform group-hover:scale-110"></div>
            
            <div className="flex items-center gap-2 mb-4 relative z-10">
                <ArrowUpCircle size={16} className="text-blue-600" />
                <h3 className="font-bold text-gray-900 text-sm">Focus Areas</h3>
            </div>

            <div className="space-y-5 relative z-10">
                {Object.entries(data.improvements).map(([category, points]) => (
                    <div key={category}>
                        <h4 className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-2">{category}</h4>
                        <ul className="space-y-3">
                            {(points as ImprovementPoint[]).map((p, i) => (
                                <li key={i} className="flex gap-2.5">
                                    <div className="mt-1.5 w-1 h-1 rounded-full bg-blue-400 shrink-0" />
                                    <div>
                                        <p className="font-bold text-gray-800 text-xs">{p.point}</p>
                                        <p className="text-xs text-gray-500 mt-1 leading-relaxed">{p.description || p.evidence}</p>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    </div>
                ))}
            </div>
        </div>

       {/* Material Reuse */}
       <div className="bg-stone-900 rounded-xl shadow-lg p-6 text-white overflow-hidden relative">
            {/* Background Texture */}
            <div className="absolute top-0 right-0 p-4 opacity-10">
                <Bookmark size={100} />
            </div>

            <div className="flex items-center justify-between mb-5 relative z-10">
                <div className="flex items-center gap-2">
                    <Bookmark size={16} className="text-yellow-500 fill-yellow-500" />
                    <h3 className="font-bold text-sm text-white">Bonus Material</h3>
                </div>
            </div>
            
            <div className="flex flex-col gap-6 relative z-10">
                <div className="space-y-3">
                    <h4 className="text-stone-500 text-[10px] font-bold uppercase tracking-widest">Applicable Themes</h4>
                    <div className="space-y-2">
                        {data.material_reuse_guide.applicable_themes.map((t, i) => (
                            <div key={i} className="bg-stone-800/50 p-2.5 rounded border border-stone-800">
                                <span className="block font-bold text-xs text-yellow-100 mb-1">{t.theme}</span>
                                <span className="text-[10px] text-stone-400 block leading-normal">{t.description}</span>
                            </div>
                        ))}
                    </div>
                </div>
                
                <div className="grid grid-cols-1 gap-4">
                    <div>
                        <h4 className="text-stone-500 text-[10px] font-bold uppercase tracking-widest mb-2">Direction</h4>
                        <p className="text-xs text-stone-300 leading-relaxed border-l-2 border-blue-500 pl-3">
                            {data.material_reuse_guide.processing_direction}
                        </p>
                    </div>
                    <div>
                        <h4 className="text-stone-500 text-[10px] font-bold uppercase tracking-widest mb-2">Expansion</h4>
                        <p className="text-xs text-stone-300 leading-relaxed border-l-2 border-green-500 pl-3">
                            {data.material_reuse_guide.expansion_ideas}
                        </p>
                    </div>
                </div>
            </div>
       </div>
    </div>
  );
};

export default AnalysisSection;