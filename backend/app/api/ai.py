from fastapi import APIRouter, Depends
from utils.jwt import get_current_user
import requests

router = APIRouter(prefix="/ai", tags=["AI"])

# =========================================================
# ⭐ 统一 AI 返回解析层（非常重要）
# =========================================================
def normalize_ai_reply(raw_response):
    """
    统一 AI 返回结果的解析层
    返回值语义：
    - str  ：自然语言（opening / followup / coach 文本）
    - dict ：结构化 JSON（single / multiple / truefalse / case / coach 评分）
    """
    if raw_response is None:
        return None

    # 来自 8002 的结构化返回
    if isinstance(raw_response, dict):
        # JSON 解析失败兜底结构
        if "raw" in raw_response:
            return raw_response.get("raw")
        return raw_response

    # 兜底转字符串
    return str(raw_response)

@router.post("/case_exam_evaluate")
def evaluate_case_exam_answer(payload: dict, current_user: dict = Depends(get_current_user)):
    role = payload.get("role", "")
    question = payload.get("question", "")
    scenario = payload.get("scenario", "")
    user_answer = payload.get("user_answer", "")
    ai_answer = payload.get("ai_answer", "")

    prompt = f"""
你是一名【企业岗位考试案例题评卷官】。

【岗位】
{role}

【案例背景】
{scenario}

【问题】
{question}

【参考答案】
{ai_answer}

【考生回答】
{user_answer}

【评分规则（总分10分）】
1. 场景理解（0-3）
2. 逻辑结构（0-3）
3. 专业判断（0-2）
4. 可执行性（0-2）

请严格只输出 JSON：
{{
  "total_score": <0-10 整数>,
  "detail": {{
    "scene": <0-3>,
    "logic": <0-3>,
    "professional": <0-2>,
    "execution": <0-2>
  }},
  "comment": "<不超过150字点评>"
}}
"""

    r = requests.post(
        "http://localhost:8002/chat",
        json={"message": prompt},
        timeout=20
    )

    data = r.json()
    normalized = normalize_ai_reply(data.get("reply"))

    if not isinstance(normalized, dict):
        raise ValueError("考试评分必须返回 JSON")

    return {
        "score": int(normalized.get("total_score", 0)),
        "detail": normalized.get("detail", {}),
        "comment": normalized.get("comment", "")
    }

# =========================================================
# AI 教练案例题评分接口
# =========================================================
@router.post("/case_evaluate")
def evaluate_case_answer(payload: dict, current_user: dict = Depends(get_current_user)):
    """
    用于训练阶段的案例/问答评分（教练式）
    不保证评分一致性，不用于正式考试
    """
    role = payload.get("role", "")
    question = payload.get("question", "")
    user_answer = payload.get("user_answer", "")
    ai_answer = payload.get("ai_answer", "")

    prompt = f"""
你是企业岗位考试的 AI 评卷官。
岗位：{role}
问题：{question}
用户回答：{user_answer}
ai生成答案: {ai_answer}
请根据岗位要求以及ai生成答案，对用户回答进行评分，满分100分，并给出简要点评。
请严格只输出一个 JSON 对象，格式如下：
{{
  "score": <整数0-100>,
  "comment": "<简要点评，不超过200字>"
}}
要求：
- 不要输出代码块或任何多余文字
- score 必须是整数
"""

    try:
        r = requests.post(
            "http://localhost:8002/chat",
            json={"message": prompt},
            timeout=15
        )
        r.raise_for_status()

        data = r.json()
        raw_response = data.get("reply") if isinstance(data, dict) else data
        normalized = normalize_ai_reply(raw_response)

        # case_evaluate 期望的是结构化 JSON
        if not isinstance(normalized, dict):
            raise ValueError(f"评卷接口期望 JSON，但收到：{normalized}")

        return {
            "score": int(normalized.get("score", 0)),
            "comment": normalized.get("comment", "")
        }

    except Exception as e:
        return {
            "score": 0,
            "comment": f"当前 AI 评卷官暂时不可用，请稍后再试。错误：{str(e)}"
        }

# =========================================================
# AI 冠军教练接口
# =========================================================
@router.post("/coach")
def coach_chat(payload: dict, current_user: dict = Depends(get_current_user)):
    role = payload.get("role", "")
    question = payload.get("question", "")

    json_structure_part = (
        '{ "reply": "<中文点评>", '
        '"score": <整数0-100>, '
        '"feedback": "<可执行建议>" }'
    )

    prompt = f"""
你是一个 AI 冠军教练，目标是根据用户回答给出专业点评、量化分数和改进建议。
岗位：{role}
用户回答：{question}

请严格只输出一个 JSON 对象：
{json_structure_part}

要求：
- 不要输出代码块或任何多余文字
- score 必须是整数
- feedback 要具体、可执行
"""

    try:
        r = requests.post(
            "http://localhost:8002/chat",
            json={"message": prompt},
            timeout=20
        )
        r.raise_for_status()

        data = r.json()
        raw_response = data.get("reply") if isinstance(data, dict) else data
        normalized = normalize_ai_reply(raw_response)

        # coach_chat 期望的是结构化 JSON
        if not isinstance(normalized, dict):
            raise ValueError(f"教练接口期望 JSON，但收到：{normalized}")

        return {
            "reply": normalized.get("reply", ""),
            "score": int(normalized.get("score", 0)),
            "feedback": normalized.get("feedback", "")
        }

    except Exception as e:
        return {
            "reply": "当前 AI 教练暂时不可用，请稍后再试。",
            "score": 0,
            "feedback": str(e)
        }


# =========================================================
# 通用出题接口
# =========================================================
@router.post("/question")
def generate_question(payload: dict, current_user: dict = Depends(get_current_user)):
    role = payload.get("role", "")
    qtype = payload.get("qtype", "followup")
    last_question = payload.get("last_question", "")
    last_answer = payload.get("last_answer", "")
    question_index = payload.get("question_index", 1)

    # ===== 构造 prompt（保持你原来的逻辑）=====
    if qtype == "opening":
        instruction = f"""
你是企业岗位考试出题官。
请根据岗位「{role}」生成一道【开场问答题】。
要求：中文，不超过30字，只输出题目。
"""
    elif qtype == "followup":
        instruction = f"""
你是企业岗位考试出题官。
岗位：{role}
上一题：{last_question}
用户回答：{last_answer}

请生成一道【追问型问答题】，不超过30字，只输出题目。
"""
    elif qtype == "single":
        instruction = f"""
你是企业岗位考试出题官。
岗位：{role}
请生成一道【单选题】，输出JSON结构如下：
{{
  "question": "<题目文本，不超过50字>",
  "options": {{ "A": "...", "B": "...", "C": "...", "D": "..." }},
  "correctAnswer": "A",
  "explanation": "<答案解析，不超过100字>"
}}
"""
    elif qtype == "multiple":
        instruction = f"""
你是企业岗位考试出题官。
岗位：{role}
请生成一道【多选题】，输出JSON结构如下：
{{
  "question": "<题目文本，不超过50字>",
  "options": {{ "A": "...", "B": "...", "C": "...", "D": "..." }},
  "correctAnswer": ["A", "B"],
  "explanation": "<答案解析，不超过100字>"
}}
"""
    elif qtype == "truefalse":
        instruction = f"""
你是企业岗位考试出题官。
岗位：{role}
请生成一道【判断题】，输出JSON结构如下：
{{
  "question": "<题目文本，不超过50字>",
  "correctAnswer": true/false,
  "explanation": "<答案解析，不超过100字>"
}}
"""
    elif qtype == "case":
        instruction = f"""
你是企业岗位考试出题官。
岗位：{role}
请生成一道【案例分析题】，输出JSON结构如下：
{{
  "question": "<问题描述，不超过100字>",
  "scenario": "<案例背景，不超过300字>",
  "correctAnswer": "<参考答案，不超过500字>",
  "explanation": "<答案解析，不超过200字>"
}}
"""
    else:
        return {"error": f"不支持的题型: {qtype}", "type": qtype}

    try:
        r = requests.post(
            "http://localhost:8002/chat",
            json={"message": instruction},
            timeout=15
        )
        r.raise_for_status()

        data = r.json()
        raw_response = data.get("reply") if isinstance(data, dict) else data
        normalized = normalize_ai_reply(raw_response)

        # ==========================
        # 以下必须是结构化 JSON
        # ==========================
        # ==========================
        # ⭐ 模型服务层兜底识别（非常关键）
        # ==========================
        if isinstance(normalized, dict) and normalized.get("error"):
            raise RuntimeError(
                f"LLM 返回错误兜底：{normalized.get('error')}"
            )


        # ==========================
        # opening / followup
        # ==========================
        if qtype in ("opening", "followup"):
            if isinstance(normalized, str) and normalized.strip():
                question_text = normalized.strip().split("\n")[0]
            else:
                question_text = f"关于{role}的第{question_index}道问答题"

            return {"nextQuestion": question_text}

        # -------- single --------
        elif qtype == "single":
            options_data = normalized.get("options", {})
            formatted_options = [
                {"id": k.lower(), "text": str(v)}
                for k, v in options_data.items()
            ]

            return {
                "type": "single",
                "question": normalized.get("question", ""),
                "options": formatted_options,
                "correctAnswer": str(normalized.get("correctAnswer", "a")).lower(),
                "explanation": normalized.get("explanation", "")
            }

        # -------- multiple --------
        elif qtype == "multiple":
            options_data = normalized.get("options", {})
            formatted_options = [
                {"id": k.lower(), "text": str(v)}
                for k, v in options_data.items()
            ]
            answers = normalized.get("correctAnswer", [])
            if not isinstance(answers, list):
                answers = [answers]

            return {
                "type": "multiple",
                "question": normalized.get("question", ""),
                "options": formatted_options,
                "correctAnswer": [str(x).lower() for x in answers],
                "explanation": normalized.get("explanation", "")
            }

        # -------- truefalse --------
        elif qtype == "truefalse":
            return {
                "type": "truefalse",
                "question": normalized.get("question", ""),
                "correctAnswer": bool(normalized.get("correctAnswer", False)),
                "explanation": normalized.get("explanation", "")
            }

        # -------- case --------
        elif qtype == "case":
            return {
                "type": "case",
                "question": normalized.get("question", ""),
                "scenario": normalized.get("scenario", ""),
                "correctAnswer": normalized.get("correctAnswer", ""),
                "explanation": normalized.get("explanation", "")
            }

    except Exception as e:
        print("生成题目出错，进入保底机制：", str(e))

        # ==========================
        # ⭐ 统一保底题目
        # ==========================
        if qtype in ("opening", "followup"):
            return {
                "nextQuestion": f"请结合岗位「{role}」说明你对核心工作的理解。"
            }

        elif qtype == "single":
            return {
                "type": "single",
                "question": f"在{role}岗位中，以下哪一项最重要？",
                "options": [
                    {"id": "a", "text": "理解业务流程"},
                    {"id": "b", "text": "只关注技术实现"},
                    {"id": "c", "text": "忽略用户需求"},
                    {"id": "d", "text": "被动等待安排"},
                ],
                "correctAnswer": "a",
                "explanation": "岗位工作的核心在于对业务流程和目标的理解。"
            }

        elif qtype == "multiple":
            return {
                "type": "multiple",
                "question": f"{role}岗位需要具备哪些能力？",
                "options": [
                    {"id": "a", "text": "业务理解"},
                    {"id": "b", "text": "沟通协作"},
                    {"id": "c", "text": "完全不与他人沟通"},
                    {"id": "d", "text": "问题分析能力"},
                ],
                "correctAnswer": ["a", "b", "d"],
                "explanation": "岗位需要综合能力，而非单一技能。"
            }

        elif qtype == "truefalse":
            return {
                "type": "truefalse",
                "question": f"{role}岗位只需要完成指派任务，不需要主动思考。",
                "correctAnswer": False,
                "explanation": "主动思考和改进是岗位的重要要求。"
            }

        elif qtype == "case":
            return {
                "type": "case",
                "question": "请分析以下工作场景并给出你的处理思路。",
                "scenario": f"你在{role}岗位中遇到业务流程不清晰、客户反馈较多的情况。",
                "correctAnswer": "应首先梳理现有业务流程，识别痛点和改进空间；其次与相关部门沟通协调，确保信息畅通；最后将复杂问题拆解成可执行的步骤，逐步推进解决。",
                "explanation": "应从业务理解、沟通协调和问题拆解角度进行分析。"
            }

        return {
            "type": qtype,
            "error": "系统暂时不可用，请稍后重试"
        }

