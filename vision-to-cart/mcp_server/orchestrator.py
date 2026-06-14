import asyncio
import time
from typing import AsyncGenerator, Dict, Any, List

# Absolute imports
from mcp_server.tool_router import ToolRouter
from mcp_server.context_manager import ContextManager
from mcp_server.confidence_governance import evaluate_confidence
from mcp_server.observability import record_metric

class Orchestrator:
    def __init__(self):
        self.tool_router = ToolRouter()
        self.context_manager = ContextManager()

    async def execute_pipeline_stream(self, payload: Any) -> AsyncGenerator[Dict[str, Any], None]:
        session_id = payload.session_id
        input_type = payload.input_type
        
        # Load or start context
        session_context = self.context_manager.get_session(session_id)
        
        # Helper event creator
        def make_event(event_type: str, label: str, data: Any = None) -> Dict[str, Any]:
            return {
                "event_type": event_type,
                "label": label,
                "data": data,
                "timestamp": time.time()
            }

        yield make_event("step_start", "Initializing pipeline workflow")
        await asyncio.sleep(0.1) # Yield time for stream responsiveness
        
        style_dna = None
        
        if input_type == "image":
            yield make_event("step_start", "Processing Image Intelligence (YOLOv8 + GPT-4o Vision)")
            
            # Call Image Tool via Router
            image_tool_input = {"image_base64": payload.image_base64, "session_id": session_id}
            style_dna_dict = await self.tool_router.call_tool("image_intelligence_tool", image_tool_input)
            
            # Convert dictionary back to StyleDNA object
            from intelligence.style_dna import StyleDNA
            style_dna = StyleDNA(**style_dna_dict)
            
            yield make_event("step_complete", "Image analyzed successfully", style_dna_dict)
            
        elif input_type == "text":
            yield make_event("step_start", "Analyzing NL Intent & Context")
            
            # Check context manager for refinements
            refined_query = self.context_manager.merge_query_with_context(session_id, payload.text_query)
            
            yield make_event("step_start", "Executing NL Understanding (Intent Schema + Web Evidence)")
            nl_tool_input = {"text_query": refined_query, "session_id": session_id}
            
            nl_output = await self.tool_router.call_tool("nl_understanding_tool", nl_tool_input)
            style_dna_dict = nl_output.get("style_dna")
            evidence = nl_output.get("evidence", [])
            
            from intelligence.style_dna import StyleDNA
            style_dna = StyleDNA(**style_dna_dict)
            
            yield make_event("step_complete", "NL understanding completed", {
                "style_dna": style_dna_dict,
                "evidence_gathered": evidence
            })

        # Save StyleDNA to session context
        self.context_manager.save_style_dna(session_id, style_dna.__dict__)
        
        # Step 2: Search & Retrieval
        yield make_event("step_start", "Performing Hybrid Database Retrieval (Vector + Keywords)")
        await asyncio.sleep(0.1)
        
        search_input = {"style_dna": style_dna.__dict__, "limit": 10}
        candidates = await self.tool_router.call_tool("search_retrieval_tool", search_input)
        
        yield make_event("step_complete", f"Retrieved {len(candidates)} candidate products", candidates)

        # Step 3: Re-ranking and Scoring
        yield make_event("step_start", "Executing 5-Component Scoring & Relevance Check")
        await asyncio.sleep(0.1)
        
        scoring_input = {"candidates": candidates, "style_dna": style_dna.__dict__}
        ranked_matches = await self.tool_router.call_tool("ranking_scoring_tool", scoring_input)
        
        yield make_event("step_complete", "Scoring & validation completed", ranked_matches)
        
        # Step 4: Confidence Governance Routing Check
        yield make_event("step_start", "Running Confidence Governance Routing")
        governed_results = evaluate_confidence(ranked_matches)
        yield make_event("step_complete", "Confidence routing applied", {
            "top_match_confidence": governed_results["top_confidence"],
            "tier": governed_results["confidence_tier"],
            "message": governed_results["governance_message"]
        })
        
        # Step 5: Recommendations Layer
        yield make_event("step_start", "Generating Budget & Premium Recommendations")
        await asyncio.sleep(0.1)
        
        rec_input = {"ranked_matches": governed_results["matches"], "style_dna": style_dna.__dict__}
        recommendations = await self.tool_router.call_tool("recommendation_tool", rec_input)
        
        yield make_event("step_complete", "Recommendations generated", recommendations)
        
        # Step 6: Final Result Ready
        final_payload = {
            "session_id": session_id,
            "style_dna": style_dna.__dict__,
            "matches": governed_results["matches"],
            "recommendations": recommendations,
            "confidence_tier": governed_results["confidence_tier"],
            "governance_message": governed_results["governance_message"]
        }
        
        # Save matches to context
        shown_ids = [m["product_id"] for m in governed_results["matches"][:3]]
        self.context_manager.save_shown_products(session_id, shown_ids)
        
        record_metric("pipelines_completed", 1)
        yield make_event("result_ready", "Workflow pipeline execution completed", final_payload)
