#!/usr/bin/env python3
"""
Test Chatbot Baseline
This test demonstrates how a simple chatbot FAILS on multi-step reasoning tasks
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent.chatbot import ChatbotBaseline

def test_chatbot():
    """Test chatbot with various queries"""
    
    print("\n" + "="*70)
    print("🤖 TESTING CHATBOT BASELINE")
    print("="*70)
    
    # Initialize chatbot
    chatbot = ChatbotBaseline()
    
    # Test queries
    test_queries = [
        # Simple questions - Chatbot should do OK
        "What is the weather in Hanoi?",
        "How much does a flight from Ho Chi Minh City to Hanoi cost?",
        
        # Complex multi-step questions - Chatbot will STRUGGLE
        "I want to fly from TP.HCM to Hanoi on April 20, stay 3 nights, find a 4-star hotel that's cheap, and I have a VIP membership. What's the total cost?",
        "Search for flights on 2026-04-20, then find hotels in Hanoi for 3 nights with 4 stars, apply VIP discount, and calculate total.",
    ]
    
    results = []
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*70}")
        print(f"Test #{i}")
        print(f"{'='*70}")
        print(f"\n📝 Query: {query[:80]}{'...' if len(query) > 80 else ''}")
        
        response = chatbot.chat(query)
        results.append(response)
        
        if response["success"]:
            print(f"\n✅ Chatbot Response:")
            print(f"   {response['response'][:200]}{'...' if len(response['response']) > 200 else ''}")
            print(f"\n⏱️  Latency: {response['latency_ms']}ms")
            print(f"📊 Tokens - Prompt: {response['tokens']['prompt_tokens']} | Completion: {response['tokens']['completion_tokens']} | Total: {response['tokens']['total_tokens']}")
        else:
            print(f"\n❌ Error: {response.get('error')}")
    
    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    success_count = sum(1 for r in results if r["success"])
    total_latency = sum(r.get("latency_ms", 0) for r in results if r["success"])
    avg_latency = total_latency // success_count if success_count > 0 else 0
    total_tokens = sum(r.get("tokens", {}).get("total_tokens", 0) for r in results if r["success"])
    
    print(f"\n✅ Successful responses: {success_count}/{len(results)}")
    print(f"⏱️  Average latency: {avg_latency}ms")
    print(f"📊 Total tokens used: {total_tokens}")
    
    print("\n🔍 ANALYSIS:")
    print("""
✅ Simple Q&A: Chatbot does OKAY (gives general answers)
❌ Multi-step tasks: Chatbot FAILS (cannot call tools, just guesses)

Why Chatbot Fails:
- No way to actually search flights ✈️
- No way to actually search hotels 🏨
- Cannot calculate exact prices without real data 💰
- Just makes up answers or gives generic responses

Next Step: Build Agent v1 with ReAct loop that CAN call tools!
    """.strip())
    
    # Save results to JSON for later analysis
    results_file = Path("logs") / "chatbot_baseline_results.json"
    Path("logs").mkdir(exist_ok=True)
    
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {results_file}")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_chatbot()
