export interface ScoreBreakdown {
  relevance: string;
  grammar_vocab: string;
  logic_structure: string;
  content: string;
}

export interface OverallEvaluation {
  tier: string;
  total_score: string;
  brief_comment: string;
  score_breakdown: ScoreBreakdown;
}

export interface HighlightPoint {
  point: string;
  evidence: string;
}

export interface Highlights {
  content: HighlightPoint[];
  language: HighlightPoint[];
  structure: HighlightPoint[];
}

export interface ImprovementPoint {
  point: string;
  description?: string;
  evidence?: string;
}

export interface Improvements {
  content: ImprovementPoint[];
  language: ImprovementPoint[];
  structure: ImprovementPoint[];
}

export interface DetailedError {
  id: number;
  type: string;
  original_sentence: string;
  correction: string;
  explanation: string;
  advanced_suggestion: string;
}

export interface Optimization {
  id: number;
  type: string;
  original_sentence: string;
  correction: string;
  explanation: string;
}

export interface ParagraphReview {
  paragraph_index: number;
  summary: string;
  issues: string;
  specific_corrections: { wrong: string; right: string }[];
}

export interface Theme {
  theme: string;
  years: string;
  description: string;
}

export interface MaterialReuseGuide {
  applicable_themes: Theme[];
  processing_direction: string;
  expansion_ideas: string;
}

export interface EssayData {
  original_text: string;
  overall_evaluation: OverallEvaluation;
  highlights: Highlights;
  improvements: Improvements;
  error_summary: {
    grammar: string[];
    spelling: string[];
    structure: string[];
  };
  detailed_errors: DetailedError[];
  optimizations: Optimization[];
  paragraph_reviews: ParagraphReview[];
  material_reuse_guide: MaterialReuseGuide;
  revised_text: string;
}
