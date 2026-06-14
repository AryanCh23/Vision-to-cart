import os
import sys
import json
import asyncio
from typing import Any

# Ensure root path is in PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server.orchestrator import Orchestrator

# Simple base64 stub for mock image search
MOCK_IMAGE_BASE64 = (
    "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////"
    "//////////////////////////////////////////////////////////////////////////"
    "///////////////////////////wgALCAAPAA8BAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP"
    "/aAAgBAQABPxA="
)

async def simulate_scenario(label: str, request_payload: Any):
    print("\n" + "="*60)
    print(f"DEMO SCENARIO: {label}")
    print("="*60)
    
    orchestrator = Orchestrator()
    print("Connecting to pipeline stream...")
    
    try:
        # Simulate receiving Server-Sent Events (SSE)
        async for event in orchestrator.execute_pipeline_stream(request_payload):
            event_type = event.get("event_type")
            step_label = event.get("label")
            data = event.get("data")
            
            if event_type == "step_start":
                print(f" [RUNNING] {step_label}...")
            elif event_type == "step_complete":
                print(f" [SUCCESS] {step_label}")
                # Print sample output context if small
                if data and isinstance(data, dict) and "style_dna" in data:
                    print(f"   -> DNA: {data['style_dna']}")
            elif event_type == "result_ready":
                print(f"\n [RESULT READY] {step_label}")
                print(f"   Confidence: {event['data']['confidence_tier']} ({event['data']['governance_message']})")
                print("\n   Top Product Matches:")
                for i, match in enumerate(event['data']['matches'][:3], 1):
                    print(f"     {i}. {match['name']} ({match['brand']}) - Price: Rs. {match['price']}")
                    print(f"        Reason: {match['match_reason']}")
                    
                print("\n   Recommendations Alternatives:")
                recs = event['data']['recommendations']
                print(f"     Budget Options: {', '.join([r['name'] for r in recs.get('budget', [])])}")
                print(f"     Premium Options: {', '.join([r['name'] for r in recs.get('premium', [])])}")
                print(f"     Trending Options: {', '.join([r['name'] for r in recs.get('trending', [])])}")
            elif event_type == "error":
                print(f" [ERROR] {step_label}: {data}")
    except Exception as e:
        print(f"Execution Error: {e}")

class MockRequest:
    def __init__(self, session_id: str, input_type: str, text_query: str = None, image_base64: str = None):
        self.session_id = session_id
        self.input_type = input_type
        self.text_query = text_query
        self.image_base64 = image_base64

async def main():
    print("==================================================")
    print("Vision-to-Cart V4 Scaffolding Demo Test Suite")
    print("==================================================")
    
    # First, run ingest to ensure local in-memory DB is initialized
    print("Initializing in-memory database...")
    from scripts.ingest_catalog import main as ingest_main
    ingest_main()

    # Scenario 1: NL Celebrity search
    req1 = MockRequest(
        session_id="session_bond_001",
        input_type="text",
        text_query="I want to buy the sunglasses Daniel Craig wore in Skyfall. Black frame preferred."
    )
    await simulate_scenario("Natural Language Celebrity Search (Daniel Craig Skyfall)", req1)
    await asyncio.sleep(1)

    # Scenario 2: Image Search simulation (Aviator)
    req2 = MockRequest(
        session_id="session_image_aviator",
        input_type="image",
        image_base64=MOCK_IMAGE_BASE64
    )
    await simulate_scenario("Image-Based Visual Search (Gold Aviator Photo)", req2)
    await asyncio.sleep(1)

    # Scenario 3: Conversational Refinement (Oakley Sport Budget)
    req3_init = MockRequest(
        session_id="session_refine_sport",
        input_type="text",
        text_query="show me some Oakley sunglasses with blue lenses for sport."
    )
    await simulate_scenario("NL Sport Query (Initial)", req3_init)
    await asyncio.sleep(1)

    req3_refine = MockRequest(
        session_id="session_refine_sport",
        input_type="text",
        text_query="make it cheaper or budget version."
    )
    await simulate_scenario("NL Sport Query (Refinement Flow)", req3_refine)

if __name__ == "__main__":
    asyncio.run(main())
