import React from 'react';
import { Wand2 } from 'lucide-react';

interface Props {
  revisedText: string;
}

const RevisedComparison: React.FC<Props> = ({ revisedText }) => {
  return (
    <div className="bg-gradient-to-br from-purple-50 via-white to-purple-50 rounded-xl shadow-sm border border-purple-100/50 overflow-hidden">
      <div className="px-5 py-4 border-b border-purple-100 flex items-center justify-between bg-white/50 backdrop-blur">
        <div className="flex items-center gap-2">
            <div className="bg-purple-100 p-1.5 rounded-md text-purple-600">
                <Wand2 size={14} />
            </div>
            <h3 className="font-bold text-sm text-purple-900">Polished Version</h3>
        </div>
      </div>
      <div className="p-6">
        <div className="prose prose-sm max-w-none font-serif text-gray-800 leading-[1.8] whitespace-pre-wrap text-justify first-letter:text-3xl first-letter:font-bold first-letter:text-purple-900 first-letter:mr-1 first-letter:float-left">
            {revisedText}
        </div>
      </div>
    </div>
  );
};

export default RevisedComparison;