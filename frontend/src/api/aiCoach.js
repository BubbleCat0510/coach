import request from './request'

// 与 AI 教练对话，获取回答、评分和反馈
export async function chatWithCoach(payload) {
	// payload: { role, question }
	try {
		const res = await request.post('/ai/coach', payload) // request 已返回 response.data
		// 兼容不同返回形态
		const reply = (res && (res.reply || res.data?.reply)) || ''
		const score = Number(res && (res.score ?? res.data?.score)) || 0
		const feedback = (res && (res.feedback || res.data?.feedback)) || ''

		return { reply, score, feedback }
	} catch (err) {
		console.error('chatWithCoach error', err)
		return { reply: 'AI 服务不可用，请稍后重试。', score: 0, feedback: '' }
	}
}

// 生成下一轮或开场问题
export async function chatWithCoachQuestion(payload) {
	// payload: { role, last_answer, type }
	return await request.post('/ai/question', payload)
}

// 获取 AI 教练分析报告
export async function getCoachReport(sessionId) {
	return await request.get('/ai/report', { params: { session_id: sessionId } })
}

// 获取案例题评分
export async function getCaseExamScore(payload) {
	return await request.post('/ai/case_exam_evaluate', payload)
}