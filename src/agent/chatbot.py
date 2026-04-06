"""
Chatbot Baseline - Without tools
A simple chatbot that tries to answer questions without using tools
This will FAIL on multi-step reasoning tasks
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.gemini_provider import GeminiProvider

class ChatbotBaseline:
    """Simple chatbot without tools"""
    
    def __init__(self, api_key: Optional[str] = None, log_dir: str = "logs"):
        """Initialize chatbot"""
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = "gemini-2.5-flash"
        self.provider = GeminiProvider(self.model_name, self.api_key)
        
        # Setup logging
        self.log_dir = log_dir
        Path(log_dir).mkdir(exist_ok=True)
        
        # Setup logger
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("chatbot_baseline")
        
        # Add file handler for detailed logs
        log_file = Path(log_dir) / f"chatbot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.logger.addHandler(file_handler)
        
        # System prompt - NO mentioning of tools
        self.system_prompt = """You are a helpful travel booking assistant.
Answer questions about travel, flights, hotels, and costs.
Provide accurate information based on your knowledge.
Be concise and helpful.
If you cannot find specific information, acknowledge it and provide your best estimation."""
    
    def chat(self, user_query: str) -> Dict[str, Any]:
        """
        Process user query and return response
        
        Returns:
        {
            "success": bool,
            "query": str,
            "response": str,
            "latency_ms": int,
            "tokens": {
                "prompt": int,
                "completion": int,
                "total": int
            }
        }
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"[QUERY] {user_query}")
            
            # Call LLM without any tools
            result = self.provider.generate(user_query, self.system_prompt)
            
            end_time = time.time()
            latency_ms = int((end_time - start_time) * 1000)
            
            response_data = {
                "success": True,
                "query": user_query,
                "response": result["content"],
                "latency_ms": latency_ms,
                "tokens": result["usage"],
                "provider": result["provider"]
            }
            
            # Log response
            self.logger.info(f"[RESPONSE] {result['content'][:100]}...")
            self.logger.info(f"[METRICS] Latency: {latency_ms}ms | Tokens: {result['usage']['total_tokens']}")
            
            return response_data
            
        except Exception as e:
            self.logger.error(f"[ERROR] {str(e)}")
            return {
                "success": False,
                "query": user_query,
                "error": str(e),
                "latency_ms": int((time.time() - start_time) * 1000)
            }
    
    def interactive_chat(self):
        """Run interactive chat session"""
        print("\n" + "="*70)
        print("🤖 CHATBOT BASELINE - Interactive Mode")
        print("="*70)
        print("Type 'quit' to exit\n")
        
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() == 'quit':
                print("Goodbye! 👋")
                break
            
            if not user_input:
                continue
            
            response = self.chat(user_input)
            print(f"\nChatbot: {response.get('response', 'No response')}")
            print(f"⏱️  Latency: {response.get('latency_ms')}ms")
            print(f"📊 Tokens: {response.get('tokens', {}).get('total', 0)}\n")
