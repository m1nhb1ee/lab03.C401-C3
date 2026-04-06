# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Lê Ngọc Hải
- **Student ID**: 2A202600380
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

**Modules Implemented**: 
- `src/tools/teaching_assistant_tools.py` - Class `CreateLearningRoadmap` (Lines 316-396)

**Code Highlights**: 
```python
class CreateLearningRoadmap(BaseTool):
    """Tool tạo lộ trình học tập"""
    
    def __init__(self):
        super().__init__(
            name="create_learning_roadmap",
            description="Tạo lộ trình học từ cơ bản -> nâng cao. Nhập topic (e.g., 'recursion', 'pointer'), target_level ('beginner', 'intermediate', 'advanced'). Trả về roadmap chi tiết với levels, concepts, tài liệu, bài tập."
        )
        self.learning_materials = self._load_learning_materials()
    
    def execute(self, topic: str = "", target_level: str = "advanced",
                include_assignments: bool = True) -> str:
        """
        Tạo lộ trình học với 3 levels: Beginner, Intermediate, Advanced
        """
```

**Documentation**: 
Tool `CreateLearningRoadmap` được thiết kế để tạo lộ trình học code từ cơ bản đến nâng cao cho sinh viên. Công cụ này:
- Nhận input: chủ đề (topic), mức độ mục tiêu (target_level), và lựa chọn bao gồm bài tập
- Tải dữ liệu từ file `data/tai_lieu_hoc_tap.json`
- Trả về một cấu trúc JSON chứa roadmap gồm 3 mức độ học tập với các khái niệm, tài liệu tham khảo, và các bài tập thực hành
- Tính toán tổng số giờ ước tính cho mỗi level

---

## II. Debugging Case Study (10 Points)

**Problem Description**: 
Trong quá trình test toàn bộ hệ thống (comprehensive_test_20260406_162056.json), scenario #4 yêu cầu: "Tôi muốn học thêm về đệ quy. Cho tôi roadmap từ cơ bản đến nâng cao." 

Thay vì agent sử dụng tool `CreateLearningRoadmap`, nó đã gọi tool `SearchLearningMaterial` để tìm kiếm keyword "recursion" rồi tự tạo ra một roadmap thủ công từ kết quả tìm kiếm.

**Log Source**: 
```json
{
  "step": 2,
  "type": "TOOL_CALL",
  "tool": "search_learning_material",
  "input": {"keyword": "recursion"},
  "observation": "{\"success\": true, \"topic\": \"Đệ Quy (Recursion)\", ...}",
  "latency_ms": 720
}
```

**Diagnosis**: 
Vấn đề này có thể là do các lý do sau:

1. **ReAct Agent không nhận biết tool CreateLearningRoadmap**: Tool có thể chưa được đăng ký đầy đủ trong danh sách tools có sẵn cho agent (trong `__all__` function có tên tool, nhưng agent có thể không biết về tham số cụ thể)

2. **Description của tool chưa rõ ràng**: Description của tool CreateLearningRoadmap sử dụng dấu ngoặc đơn `()` trong cách mô tả mức độ, có thể gây confusion cho LLM:
   ```
   "target_level ('beginner', 'intermediate', 'advanced')"
   ```

3. **Agent tự sinh roadmap thay vì dùng tool**: Khi agent không tìm thấy cách gọi tool CreateLearningRoadmap một cách rõ ràng, nó đã sử dụng kết quả từ SearchLearningMaterial để tự tạo roadmap, điều này vẫn trả về kết quả đúng nhưng không sử dụng tool đúng mục đích

4. **Không có explicit tool registration**: Tool CreateLearningRoadmap có thể cần được đăng ký/import rõ ràng hơn trong hệ thống agent để LLM biết nên gọi nó

**Solution**: 

Để khắc phục vấn đề này, nên thực hiện:

1. **Cung cấp mô tả tool rõ ràng hơn**:
   ```python
   description="Tạo lộ trình học tập chi tiết từ cơ bản đến nâng cao. Nhập: topic (ví dụ: 'recursion', 'pointer'), target_level (chọn: beginner, intermediate, hoặc advanced). Trả về roadmap chi tiết gồm các mức độ học, khái niệm, tài liệu tham khảo, và bài tập."
   ```

2. **Kiểm tra tool registration**: Đảm bảo tool được exported trong `__all__` list (đã có) và được load vào agent context đúng cách

3. **Thêm validation và error handling tốt hơn**:
   ```python
   # Validate target_level
   valid_levels = ["beginner", "intermediate", "advanced"]
   if target_level not in valid_levels:
       return json.dumps({
           "success": False,
           "error": f"target_level phải là một trong: {valid_levels}"
       }, ensure_ascii=False)
   ```

4. **Cấu trúc roadmap linh hoạt hơn**: Thay vì roadmap luôn có 3 levels cố định, nên:
   - Nếu target_level = "beginner" → chỉ trả Beginner level
   - Nếu target_level = "intermediate" → trả Beginner + Intermediate
   - Nếu target_level = "advanced" → trả cả 3 levels

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

### 1. Reasoning - Vai trò của Thought block

**Chatbot vs Tool-specific Agent**:
- **Chatbot** (baseline): Trả lời direct, không qua trình suy luận, cho kết quả tương đối chung chung. Ví dụ với query "Cho tôi roadmap", chatbot liệt kê 8 phần với giải thích dài dòng
- **ReAct Agent với CreateLearningRoadmap**: Khi được tích hợp đúng, agent sẽ:
  - **Thought**: "Người dùng yêu cầu roadmap học đệ quy từ cơ bản đến nâng cao → cần sử dụng tool CreateLearningRoadmap"
  - **Action**: Gọi `create_learning_roadmap(topic="recursion", target_level="advanced")`
  - **Observation**: Nhận kết quả JSON có cấu trúc từ tool
  - **Final Answer**: Format kết quả thành câu trả lời dễ hiểu

Việc có Thought block giúp agent rõ ràng:
- Khi nào cần dùng tool nào
- Parameter nào cần truyền vào
- Cách xử lý kết quả từ tool

### 2. Reliability - Khi nào Agent kém hơn Chatbot

Trong test hiện tại, agent **chưa** có điểm yếu so với chatbot cho scenario này vì:
- Agent vẫn trả về roadmap hợp lý, chỉ không dùng tool chính xác (đây là vấn đề effectiveness, không phải correctness)
- Chatbot không có cơ chế để truy cập dữ liệu có cấu trúc từ tool

Tuy nhiên, nếu tool CreateLearningRoadmap được tích hợp đúng, agent sẽ tốt hơn vì:
- Pre-computed roadmap từ dữ liệu có cấu trúc
- Consistency giữa các request
- Dễ update dữ liệu mà không cần thay LLM

### 3. Observation - Tác động của Environment Feedback

Trong scenario #2 (query về trừ điểm nộp trễ):
- **Agent**: 
  - Bước 1: Nhận query "Tôi nộp bài muộn 2 ngày"
  - Parse Error lần đầu (agent không format response đúng pattern)
  - Bước 2: Tool call `get_course_policy(policy_type="late_submission")`
  - Observation trả về: `{"success": true, ...chi tiết trừ điểm...}`
  - Bước 3: Agent sử dụng observation này để đưa ra final answer chính xác

Observation từ tool giúp agent **correct** từ lần thử đầu theo một cách structural:
- Không cần hallucinate deadline
- Recovery từ parse error bằng cách gọi đúng tool

---

## IV. Future Improvements (5 Points)

### 1. Scalability

**Hiện tại**:
- Roadmap cứng nhắc với 3 levels cố định
- Tài liệu load từ file JSON (single file)

**Cải thiện**:
```python
# Sử dụng Vector DB (ví dụ: Qdrant, Weaviate)
# Để tìm kiếm tài liệu liên quan theo semantic similarity
from qdrant_client import QdrantClient
vector_db = QdrantClient(path="/path/to/qdrant")

def get_relevant_resources(topic: str, level: str) -> List[str]:
    embeddings = generate_embeddings(topic)
    search_results = vector_db.search(embeddings, limit=10)
    return [r.payload['resource'] for r in search_results if r.payload['level'] == level]
```

### 2. Safety

**Hiện tại**:
- Không có validation input quá sâu
- Không giới hạn độ dài output

**Cải thiện**:
```python
# Validator class
class RoadmapValidator:
    MAX_HOURS_PER_LEVEL = 100
    ALLOWED_TOPICS = ["pointer", "recursion", "array", "string", "memory", "buffer_overflow"]
    
    def validate_request(self, topic: str, target_level: str) -> Tuple[bool, str]:
        if topic not in self.ALLOWED_TOPICS:
            return False, f"Topic '{topic}' not supported. Use: {self.ALLOWED_TOPICS}"
        if target_level not in ["beginner", "intermediate", "advanced"]:
            return False, "Invalid target_level"
        return True, ""
```

### 3. Performance

**Hiện tại**:
- JSON load mỗi lần execute method được gọi (nếu không cache)
- Không có pagination cho roadmap lớn

**Cải thiện**:
```python
# Async tool execution
import asyncio

class CreateLearningRoadmapAsync(BaseTool):
    async def execute_async(self, topic: str = "", target_level: str = "advanced", 
                           include_assignments: bool = True) -> str:
        # Load từ cache hoặc database
        material = await self._load_learning_materials_async()
        roadmap = await asyncio.gather(
            self._generate_beginner_level(material),
            self._generate_intermediate_level(material),
            self._generate_advanced_level(material)
        )
        return json.dumps({
            "success": True,
            "topic": topic,
            "roadmap": roadmap
        }, ensure_ascii=False)

# Async trong Agent loop
result = await agent.execute_tool_async(tool_name, **params)
```

### 4. Additional Improvements

- **Personalization**: Ghi nhớ level hiện tại của sinh viên, suggest next steps
- **Interactive Roadmap**: Thêm link tới bài tập, quiz, track progress
- **Multi-language Support**: Roadmap cho tiếng Anh, Anh, Mandarin, v.v.
- **Feedback Loop**: Sinh viên đánh giá roadmap → tune lại dữ liệu

---

## Summary

Tool `CreateLearningRoadmap` là một thành phần tốt cho hệ thống trợ giảng ReAct, tuy nhiên hiện tại chưa được tích hợp hoàn toàn vào agent. Vấn đề chính là:

1. **Integration Issue**: Agent không gọi tool này cho scenario roadmap
2. **Clarity Issue**: Description tool cần rõ ràng hơn
3. **Flexibility Issue**: Cấu trúc roadmap cứng nhắc, cần linh hoạt hơn

Khi các vấn đề này được giải quyết, tool sẽ cung cấp giá trị lớn cho sinh viên thông qua:
- Cấu trúc học tập rõ ràng
- Tài liệu được curation
- Bài tập phù hợp từng level

---

> **Note**: Báo cáo này dựa trên phân tích source code (teaching_assistant_tools.py lines 316-396) và test logs (comprehensive_test_20260406_162056.json), đặc biệt là scenario #4 liên quan đến CreateLearningRoadmap.
