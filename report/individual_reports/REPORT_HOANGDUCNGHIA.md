# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Hoàng Đức Nghĩa
- **Student ID**: 2A202600371
- **Date**: 06/04/2026

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.).*

- **Modules Implementated**: src/tools/course_policy.py
- **Code Highlights**:
json_path = os.path.join(os.path.dirname(__file__), '..', '..', 'quy_dinh_mon_hoc.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            policies = json.load(f)
- **Documentation**: Tạo một tool để giúp ReAct loop có thể sao chéo với quy định về "deadline", "scoring", "late submission", "grading" và "attendance" nhanh hơn so với chatbot

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: File tool không thể liên kết với file test
- **Log Source**: lab03.C401-C3\logs\2026-04-06.log
- **Diagnosis**: Lỗi do hàm get_course_policy được định nghĩa ở hai nơi (agent.py và tools/get_course_policy.py), khiến tool không thể truy cập đúng file. LLM có thể bị confuse bởi tool spec không nhất quán.
- **Solution**: Refactor code bằng cách loại bỏ duplicate function khỏi agent.py và import từ tools module. Thêm logging để track tool calls và test results.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: "Thought" giúp nâng cao khả năng reasoning của ReAct so với chatbot. Thay vì cho câu trả lời luôn, agent chia vấn đề thành các bước khác nhau(reasoning → action → observation). Điều này giúp cho câu trả lời chính xác, hoàn thiện hơn.
2.  **Reliability**: Trường hợp Agent làm kém hơn Chatbot là đối với các câu hỏi đơn giản, Agent có thể làm phức tạp hóa vấn đề, dẫn đến việc tốn thời gian, resource hơn Chatbot
3.  **Observation**: Observations giúp cho Agent flexible hơn Chatbot. Observation giúp Agent chỉnh sửa reasoning một cách linh hoạt hơn, xác nhận giả định và hoàn thiện câu trả lời dựa trên data thật.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Sử dụng hàng đợi bất đồng bộ để xử lý tool calls và horizontal scaling để xử lí nhiều user đồng bộ
- **Safety**: Thêm guardrails để giới hạn số bước reasoning và
whitelist tool được phép dùng
- **Performance**: Batch request và streaming response để giảm latency

---


