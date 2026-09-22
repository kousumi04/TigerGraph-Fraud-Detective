# backend/app/api/streaming.py
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..agent.workflow import build_investigation_graph

router = APIRouter()
logger = logging.getLogger(__name__)
graph = build_investigation_graph()

@router.websocket("/ws/cases/{case_id}/stream")
async def stream_investigation(websocket: WebSocket, case_id: str):
    """
    Streams the node-by-node execution of the LangGraph agent directly to the UI.
    Expects an initial JSON payload with the trigger data to start.
    """
    await websocket.accept()
    
    try:
        # Wait for the client to send the trigger context
        data = await websocket.receive_text()
        trigger_data = json.loads(data)
        
        initial_state = {
            "case_id": case_id,
            "trigger": trigger_data,
            "tool_calls": 0,
            "tokens": 0,
            "errors": []
        }
        
        # Asynchronously stream graph updates
        async for output in graph.astream(initial_state):
            # Output is a dict mapping node_name -> state_updates
            for node_name, state_update in output.items():
                event = {
                    "node": node_name,
                    "status": "completed",
                    # Strip out massive data structures for the UI stream if needed, 
                    # or send specific summary fields
                    "updates_summary": list(state_update.keys())
                }
                await websocket.send_json(event)
                
        await websocket.send_json({"node": "END", "status": "investigation_complete"})
        
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for case {case_id}")
    except Exception as e:
        logger.error(f"Streaming error for {case_id}: {e}")
        await websocket.send_json({"error": str(e)})
        await websocket.close()