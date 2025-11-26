import React, { useState, useEffect } from 'react';
import { EssayData, DetailedError, Optimization } from '../types';
import { Check, Lightbulb, Sparkles } from 'lucide-react';

interface Props {
  data: EssayData;
}

type Annotation = {
  id: string; 
  displayId: number; 
  start: number;
  end: number;
  type: 'error' | 'optimization';
  data: DetailedError | Optimization;
};

const AnnotatedEssay: React.FC<Props> = ({ data }) => {
  const [annotations, setAnnotations] = useState<Annotation[]>([]);
  const [segments, setSegments] = useState<(string | { text: string; annotation: Annotation })[]>([]);

  useEffect(() => {
    const foundAnnotations: Annotation[] = [];
    const fullText = data.original_text;

    const addAnnotation = (item: DetailedError | Optimization, type: 'error' | 'optimization') => {
      let snippet = item.original_sentence.trim();
      let index = fullText.indexOf(snippet);
      
      // Simple fuzzy fallback: try removing last char (often punctuation mismatch)
      if (index === -1 && snippet.length > 5) {
          index = fullText.indexOf(snippet.slice(0, -1));
      }

      if (index !== -1) {
        foundAnnotations.push({
          id: `${type}-${item.id}`,
          displayId: 0, 
          start: index,
          end: index + snippet.length,
          type,
          data: item,
        });
      }
    };

    data.detailed_errors.forEach(err => addAnnotation(err, 'error'));
    data.optimizations.forEach(opt => addAnnotation(opt, 'optimization'));

    // Sort by position in text (Reader Flow)
    foundAnnotations.sort((a, b) => a.start - b.start);
    foundAnnotations.forEach((ann, idx) => ann.displayId = idx + 1);

    setAnnotations(foundAnnotations);

    // Segment text for highlighting
    const newSegments: (string | { text: string; annotation: Annotation })[] = [];
    let currentIdx = 0;

    foundAnnotations.forEach(ann => {
      if (ann.start > currentIdx) {
        newSegments.push(fullText.slice(currentIdx, ann.start));
      }
      newSegments.push({
        text: fullText.slice(ann.start, ann.end),
        annotation: ann
      });
      currentIdx = ann.end;
    });

    if (currentIdx < fullText.length) {
      newSegments.push(fullText.slice(currentIdx));
    }

    setSegments(newSegments);
  }, [data]);

  return (
    <div className="flex flex-col gap-8">
      {/* 1. Essay Text Block */}
      <div className="relative">
         {/* Paper Background Effect */}
         <div className="bg-[#fffdf9] p-6 rounded-xl border border-stone-100 shadow-[2px_4px_16px_rgba(0,0,0,0.03)] relative overflow-hidden">
             {/* Lines Pattern */}
             <div className="absolute inset-0 opacity-[0.03] pointer-events-none" 
                  style={{ backgroundImage: 'linear-gradient(#000 1px, transparent 1px)', backgroundSize: '100% 28px' }}>
             </div>

             <div className="font-serif text-[17px] leading-[1.8] text-gray-800 whitespace-pre-wrap text-justify relative z-10">
                {segments.map((segment, idx) => {
                    if (typeof segment === 'string') return <span key={idx}>{segment}</span>;
                    
                    const isError = segment.annotation.type === 'error';
                    const ann = segment.annotation;
                    
                    return (
                    <span key={idx} className="relative inline-block mx-0.5 group">
                        <span className={`
                        border-b-2 pb-0.5 cursor-help transition-colors duration-200
                        ${isError 
                            ? 'border-red-400/50 bg-red-50/50 text-gray-900 group-hover:bg-red-100' 
                            : 'border-blue-400/50 bg-blue-50/50 text-gray-900 group-hover:bg-blue-100'
                        }
                        `}>
                        {segment.text}
                        </span>
                        <sup className={`
                            ml-0.5 font-sans text-[9px] font-bold px-1.5 py-0.5 rounded-full align-top shadow-sm select-none
                            ${isError ? 'text-white bg-red-500' : 'text-white bg-blue-500'}
                        `}>
                            {ann.displayId}
                        </sup>
                    </span>
                    );
                })}
            </div>
         </div>
      </div>

      {/* 2. Annotations List Stream */}
      <div className="space-y-4">
          <div className="flex items-center justify-between px-1">
             <h3 className="text-xs font-bold text-gray-400 uppercase tracking-widest">
                Review Comments ({annotations.length})
             </h3>
          </div>

          {annotations.map((ann) => {
              const isError = ann.type === 'error';
              const detail = ann.data;

              return (
              <div
                  key={ann.id}
                  className={`
                  p-5 rounded-xl border bg-white shadow-sm transition-all duration-300
                  ${isError ? 'border-l-[3px] border-l-red-500 border-stone-100' : 'border-l-[3px] border-l-blue-500 border-stone-100'}
                  `}
              >
                  <div className="flex items-start gap-4">
                      {/* ID Badge */}
                      <div className={`
                          flex items-center justify-center w-6 h-6 rounded-full text-[11px] font-bold shrink-0 shadow-sm
                          ${isError ? 'bg-red-500 text-white' : 'bg-blue-500 text-white'}
                      `}>
                          {ann.displayId}
                      </div>
                      
                      <div className="flex-1 min-w-0 space-y-3">
                          {/* Header: Type & Original Text */}
                          <div>
                            <div className="flex justify-between items-center mb-1">
                                <span className={`text-[10px] font-bold uppercase tracking-wider ${isError ? 'text-red-500' : 'text-blue-500'}`}>
                                    {isError ? (detail as DetailedError).type : 'Expressive Upgrade'}
                                </span>
                            </div>
                            <div className="text-xs text-gray-400 font-serif line-through decoration-gray-300 truncate opacity-80">
                                {detail.original_sentence}
                            </div>
                          </div>

                          {/* Correction */}
                          <div className="flex items-start gap-2.5 bg-stone-50/50 p-2.5 rounded-lg border border-stone-100">
                              <Check size={16} className="text-green-600 mt-0.5 shrink-0" />
                              <span className="text-stone-800 font-bold text-sm leading-snug font-serif">
                                {detail.correction}
                              </span>
                          </div>

                          {/* Explanation */}
                          <p className="text-xs text-stone-500 leading-relaxed pl-1">
                              {detail.explanation}
                          </p>

                          {/* Advanced Suggestion Block (New Design) */}
                          {isError && (detail as DetailedError).advanced_suggestion && (
                              <div className="mt-2 relative overflow-hidden rounded-lg bg-gradient-to-br from-indigo-50 to-purple-50 border border-indigo-100/50 p-3">
                                  {/* Decorative icon background */}
                                  <Sparkles className="absolute -right-1 -top-1 text-indigo-100 w-8 h-8 rotate-12" />
                                  
                                  <div className="relative z-10 flex flex-col gap-1.5">
                                      <div className="flex items-center gap-1.5">
                                          <Lightbulb size={12} className="text-indigo-600 fill-indigo-600" />
                                          <span className="text-[10px] font-bold uppercase tracking-widest text-indigo-700">
                                            Advanced Insight
                                          </span>
                                      </div>
                                      <p className="text-xs text-indigo-900 font-serif italic leading-relaxed">
                                          "{(detail as DetailedError).advanced_suggestion}"
                                      </p>
                                  </div>
                              </div>
                          )}
                      </div>
                  </div>
              </div>
              );
          })}
      </div>
    </div>
  );
};

export default AnnotatedEssay;