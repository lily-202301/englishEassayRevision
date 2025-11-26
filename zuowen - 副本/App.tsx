import React, { useEffect, useState } from 'react';
import { MOCK_DATA } from './constants';
import { EssayData } from './types';
import ScoreOverview from './components/ScoreOverview';
import AnnotatedEssay from './components/AnnotatedEssay';
import AnalysisSection from './components/AnalysisSection';
import RevisedComparison from './components/RevisedComparison';
import { GraduationCap, Printer } from 'lucide-react';

const App: React.FC = () => {
  const [data, setData] = useState<EssayData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handlePrint = () => {
    window.print();
  };

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch('/qwen_essay_result.json');
        if (!res.ok) throw new Error(`fetch failed: ${res.status}`);
        const json = (await res.json()) as EssayData;
        setData(json);
      } catch (err) {
        console.error(err);
        setError('加载最新评测数据失败，使用内置示例数据');
        setData(MOCK_DATA);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-600">
        正在加载评测数据…
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center text-red-600">
        数据加载失败
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-stone-100 py-0 md:py-8 flex justify-center font-sans text-gray-900">
      <div className="w-full max-w-xl bg-white shadow-2xl md:rounded-[2rem] overflow-hidden min-h-screen flex flex-col border border-stone-200/60">
        <div className="no-print absolute top-4 right-4 z-50 flex gap-2">
          <button
            onClick={handlePrint}
            className="flex items-center justify-center w-10 h-10 bg-black/80 backdrop-blur text-white rounded-full shadow-lg hover:bg-black transition-all"
            title="导出 PDF / 打印"
          >
            <Printer size={18} />
          </button>
        </div>

        <header className="bg-stone-900 text-white p-8 pb-12 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full blur-3xl -mr-16 -mt-16"></div>
          <div className="absolute bottom-0 left-0 w-40 h-40 bg-blue-500/10 rounded-full blur-2xl -ml-10 -mb-10"></div>

          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-6 opacity-80">
              <GraduationCap size={24} />
              <span className="text-xs font-bold tracking-[0.2em] uppercase">Smart Assessment</span>
            </div>
            <h1 className="text-3xl font-serif font-bold mb-2 leading-tight">
              英语作文
              <br />
              深度评估报告
            </h1>
            <div className="w-12 h-1 bg-blue-500 mt-4 mb-6"></div>
            <div className="flex justify-between items-end text-sm text-stone-400">
              <div>
                <p className="uppercase tracking-wider text-[10px] mb-1">Generated</p>
                <p className="font-serif text-stone-200">{new Date().toLocaleDateString('zh-CN')}</p>
              </div>
              <div className="text-right">
                <p className="uppercase tracking-wider text-[10px] mb-1">ID</p>
                <p className="font-mono text-stone-200">#8291-A</p>
              </div>
            </div>
          </div>
        </header>

        <main className="flex-grow bg-white relative -mt-6 rounded-t-[2rem] px-6 pt-8 pb-12 space-y-10 shadow-[0_-10px_40px_rgba(0,0,0,0.1)]">
          {error && (
            <div className="no-print bg-amber-50 border border-amber-200 text-amber-700 text-sm px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <section>
            <ScoreOverview evaluation={data.overall_evaluation} />
          </section>

          <div className="flex items-center gap-4 opacity-30">
            <div className="h-px bg-stone-900 flex-1"></div>
            <span className="font-serif italic text-xs">Section 01</span>
            <div className="h-px bg-stone-900 flex-1"></div>
          </div>

          <section>
            <div className="mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-1">逐句精批与原文</h2>
              <p className="text-xs text-gray-400 uppercase tracking-widest">Detailed Annotations</p>
            </div>
            <AnnotatedEssay data={data} />
          </section>

          <div className="flex items-center gap-4 opacity-30">
            <div className="h-px bg-stone-900 flex-1"></div>
            <span className="font-serif italic text-xs">Section 02</span>
            <div className="h-px bg-stone-900 flex-1"></div>
          </div>

          <section>
            <div className="mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-1">深度点评与拓展</h2>
              <p className="text-xs text-gray-400 uppercase tracking-widest">Deep Analysis</p>
            </div>
            <AnalysisSection data={data} />
          </section>

          <div className="flex items-center gap-4 opacity-30">
            <div className="h-px bg-stone-900 flex-1"></div>
            <span className="font-serif italic text-xs">Section 03</span>
            <div className="h-px bg-stone-900 flex-1"></div>
          </div>

          <section>
            <div className="mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-1">高分范文润色</h2>
              <p className="text-xs text-gray-400 uppercase tracking-widest">Polished Revision</p>
            </div>
            <RevisedComparison revisedText={data.revised_text} />
          </section>
        </main>

        <footer className="bg-stone-50 p-8 text-center border-t border-stone-100">
          <div className="flex items-center justify-center gap-2 text-stone-400 mb-4">
            <div className="w-1 h-1 rounded-full bg-stone-300"></div>
            <div className="w-1 h-1 rounded-full bg-stone-300"></div>
            <div className="w-1 h-1 rounded-full bg-stone-300"></div>
          </div>
          <p className="text-[10px] text-stone-400 uppercase tracking-[0.2em]">AI Intelligent Engine</p>
        </footer>
      </div>
    </div>
  );
};

export default App;
