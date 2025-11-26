import { EssayData } from './types';

export const MOCK_DATA: EssayData = {
  "original_text": "We sat down next to each other, but David wouldn't look at me. I tried to talked to him nicely and patiently, \"Come on, David. Tell me what bothers you so much that you decided to quit. You practiced so hard for the run.\" David glimpsed at me and lowered his head, seeming anxious and frustrated. \"I'm just concerned that others will laugh at me because of the way I run.\" I understood David's worries and made efforst to light up his moud and encourage him to go back to the race. \"No one's going to laugh at you as long as you show your determination and faith. I'm sure the crowd will cheer for you.\" Having heard this, a flood of excitement and hope streamed in David's heart. He stood up as his eyes sharpened, \"I'm ready.\" \n\nI watched as David moved up to the starting line with the other runners. As the judge shot, all the runners dashed out like an arrow except David, managing to control his body well. David made his maximum efforts to",
  "overall_evaluation": {
    "tier": "第四档 (15-17分)",
    "total_score": "16/25",
    "brief_comment": "文章情节发展合理，能够紧扣原文情感脉络。学生尝试使用了心理描写和对话描写，但基础语法错误较多（如不定式后跟过去式、拼写错误），且部分表达带有明显的中式英语痕迹。",
    "score_breakdown": {
      "relevance": "切题，能够延续原文的故事情节。",
      "grammar_vocab": "词汇量尚可，但拼写和基础语法错误频发，影响阅读流畅度。",
      "logic_structure": "段落结构清晰，第一段解决心理障碍，第二段开始比赛，逻辑通顺。",
      "content": "内容较为充实，特别是第一段的对话设计较好，但结尾处戛然而止（因字数或时间限制），不够完整。"
    }
  },
  "highlights": {
    "content": [
      {
        "point": "情感转变自然",
        "evidence": "从'David wouldn't look at me'到'eyes sharpened, I'm ready'，刻画了David从自卑到重拾信心的过程。"
      }
    ],
    "language": [
      {
        "point": "尝试使用高级词汇与修辞",
        "evidence": "使用了'glimpsed', 'anxious and frustrated', 'flood of excitement', 'eyes sharpened'等表达，增强了画面的生动性。"
      }
    ],
    "structure": [
      {
        "point": "对话引导情节",
        "evidence": "利用老师的鼓励和David的回应有效地推动了故事发展，过渡自然。"
      }
    ]
  },
  "improvements": {
    "content": [
      {
        "point": "结尾完整性",
        "description": "第二段明显未写完，缺乏对David奔跑过程的具体描写以及比赛结束后的反应，这是续写的重要部分。"
      }
    ],
    "language": [
      {
        "point": "消除中式英语",
        "evidence": "原文'light up his moud' (点亮心情?) 和 'judge shot' (裁判开枪?) 需要转换为地道的英语表达。"
      },
      {
        "point": "基础拼写与语法",
        "evidence": "'talked', 'efforst', 'moud'等低级错误需要避免。"
      }
    ],
    "structure": [
      {
        "point": "动作描写的连贯性",
        "description": "第二段起跑时的描写略显生硬，'except David'的位置安排让句子显得头重脚轻。"
      }
    ]
  },
  "error_summary": {
    "grammar": [
      "不定式错误 (to talked)",
      "主谓一致与单复数 (dashed out like an arrow)"
    ],
    "spelling": [
      "efforst -> efforts",
      "moud -> mood"
    ],
    "structure": [
      "搭配不当 (light up mood, judge shot)"
    ]
  },
  "detailed_errors": [
    {
      "id": 1,
      "type": "语法错误",
      "original_sentence": "I tried to talked to him nicely and patiently",
      "correction": "I tried to talk to him nicely and patiently",
      "explanation": "不定式 'to' 后面必须跟动词原形。",
      "advanced_suggestion": "I attempted to communicate with him gently and patiently..."
    },
    {
      "id": 2,
      "type": "拼写错误",
      "original_sentence": "made efforst to light up his moud",
      "correction": "made efforts to lift his spirits/mood",
      "explanation": "'efforst' 拼写错误，应为 'efforts'；'moud' 拼写错误，应为 'mood'；且 'light up his mood' 搭配不地道，常用 'lift his spirits' 或 'cheer him up'。",
      "advanced_suggestion": "made every effort to lift his spirits..."
    },
    {
      "id": 3,
      "type": "搭配不当",
      "original_sentence": "a flood of excitement and hope streamed in David's heart",
      "correction": "a flood of excitement and hope surged through David",
      "explanation": "'streamed in... heart' 表达略显中式，情感涌动常用 'surged through' 或 'welled up in'。",
      "advanced_suggestion": "a wave of excitement and hope washed over David."
    },
    {
      "id": 4,
      "type": "中式英语",
      "original_sentence": "As the judge shot",
      "correction": "As the starting gun fired",
      "explanation": "'judge shot' 直译自中文“裁判开枪”，语境不当（像是在射击）。比赛开始应指枪响。",
      "advanced_suggestion": "The moment the starting pistol cracked..."
    },
    {
      "id": 5,
      "type": "语法错误",
      "original_sentence": "all the runners dashed out like an arrow",
      "correction": "all the runners dashed out like arrows",
      "explanation": "主语 'runners' 是复数，喻体 'arrow' 也应对应复数，或者使用 'shot out like an arrow from a bow' (作为整体动作)。",
      "advanced_suggestion": "dashed out like arrows from a bow..."
    }
  ],
  "optimizations": [
    {
      "id": 1,
      "type": "句式升级",
      "original_sentence": "David glimpsed at me and lowered his head, seeming anxious and frustrated.",
      "correction": "David stole a glance at me before burying his head in his hands, a mixture of anxiety and frustration written all over him.",
      "explanation": "原句表达清楚但略显平淡。升格后增加了动作细节（burying his head）和神态描写（written all over him），更具画面感。"
    },
    {
      "id": 2,
      "type": "句式升级",
      "original_sentence": "He stood up as his eyes sharpened, \"I'm ready.\"",
      "correction": "He stood up, a newfound determination gleaming in his eyes. \"I'm ready,\" he declared firmly.",
      "explanation": "将单纯的 'sharpened' 改为 'newfound determination gleaming'，并增加了说话的语气 'declared firmly'，增强了人物的坚定感。"
    }
  ],
  "paragraph_reviews": [
    {
      "paragraph_index": 1,
      "summary": "描写了“我”鼓励David的过程以及David心理状态的转变。",
      "issues": "存在明显的拼写错误和不定式语法错误，部分短语搭配不地道。",
      "specific_corrections": [
        {
          "wrong": "to talked",
          "right": "to talk"
        },
        {
          "wrong": "efforst",
          "right": "efforts"
        },
        {
          "wrong": "moud",
          "right": "mood"
        }
      ]
    },
    {
      "paragraph_index": 2,
      "summary": "描写了比赛开始的情景，David与其他选手的对比。",
      "issues": "出现了典型的中式英语表达（judge shot），且段落未完成，句子中断。",
      "specific_corrections": [
        {
          "wrong": "judge shot",
          "right": "gun fired / pistol went off"
        },
        {
          "wrong": "like an arrow",
          "right": "like arrows"
        }
      ]
    }
  ],
  "material_reuse_guide": {
    "applicable_themes": [
      {
        "theme": "克服困难 (Overcoming Adversity)",
        "years": "2021新高考I卷, 2022全国甲卷",
        "description": "适用于描写人物面对身体缺陷或心理障碍时，在他人鼓励下重拾信心的场景。"
      },
      {
        "theme": "师生情谊 (Teacher-Student Relationship)",
        "years": "常见于各类模拟题",
        "description": "适用于描写老师通过耐心引导帮助学生走出困境的情节。"
      }
    ],
    "processing_direction": "积累关于“鼓励”、“眼神变化”、“起跑动作”的地道表达，替换文中生硬的中式英语。",
    "expansion_ideas": "可以将本文中David起跑后的心理活动以及艰难奔跑但坚持到底的细节作为后续练习的重点，例如描写他如何摔倒又爬起，周围人的反应等。"
  },
  "revised_text": "We sat down next to each other, but David wouldn't look at me. I tried to talk to him nicely and patiently, \"Come on, David. Tell me what bothers you so much that you decided to quit. You practiced so hard for the run.\" David glanced at me and lowered his head, looking anxious and frustrated. \"I'm just concerned that others will laugh at me because of the way I run.\" Understanding David's worries, I made every effort to lift his spirits and encourage him to return to the race. \"No one is going to laugh at you as long as you show your determination and faith. I'm sure the crowd will cheer for you.\" Hearing this, a flood of excitement and hope surged through David. He stood up, his eyes shining with newfound determination, and said firmly, \"I'm ready.\"\n\nI watched as David moved up to the starting line with the other runners. The moment the starting gun fired, all the runners shot out like arrows. Unlike the others, David started slowly, managing to control his body with great focus. Although he lagged behind, he made his maximum effort to maintain his balance and rhythm. The crowd, initially quiet, began to clap as they saw his persistence. He wasn't running for speed; he was running for dignity. With sweat streaming down his face, David crossed the finish line, not first in the race, but a true champion in life."
};