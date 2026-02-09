"""Opik observability integration for tracking LLM calls and metrics."""
import os
import logging
from typing import Optional, Dict, Any
from functools import wraps
import time
import asyncio

try:
    import opik
    from opik import track
    OPIK_AVAILABLE = True
except ImportError:
    OPIK_AVAILABLE = False
    logging.warning("Opik not installed. Observability disabled.")

logger = logging.getLogger(__name__)


class OpikTracker:
    """Singleton tracker for Opik observability."""
    
    _instance: Optional['OpikTracker'] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        if not OPIK_AVAILABLE:
            logger.warning("Opik SDK not available - observability disabled")
            self._initialized = True
            return
        
        try:
            api_key = os.getenv("OPIK_API_KEY")
            workspace = os.getenv("OPIK_WORKSPACE", "default")
            
            if api_key:
                # Configure Opik Client
                from opik import Opik
                self.client = Opik(
                    api_key=api_key,
                    workspace=workspace,
                    project_name=os.getenv("OPIK_PROJECT_NAME", "vina-mvp")
                )
                logger.info(f"✅ Opik initialized - workspace: {workspace}")
                self._initialized = True
            else:
                logger.warning("OPIK_API_KEY not set - observability disabled")
                self._initialized = True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Opik: {e}")
            self._initialized = True
        
        # In-memory storage for session cost tracking (Split-by-Split)
        if not hasattr(self, "session_costs"):
            self.session_costs = []
    
    def log_trace(
        self,
        name: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[list] = None
    ):
        """Log a trace to Opik."""
        if not OPIK_AVAILABLE or not hasattr(self, 'client'):
            return
        
        try:
            self.client.trace(
                name=name,
                input=input_data,
                output=output_data,
                metadata=metadata or {},
                tags=tags or []
            )
            logger.debug(f"📊 Logged trace: {name}")
            
            # Track cost in session (for immediate reporting)
            if metadata and "estimated_cost" in metadata:
                try:
                    self.session_costs.append({
                        "operation": name,
                        "cost": float(metadata["estimated_cost"]),
                        "service": metadata.get("service", "llm"),
                        "unit": metadata.get("usage_unit", "tokens"),
                        "amount": metadata.get("usage_amount", 0)
                    })
                except Exception as e:
                    logger.warning(f"Failed to track session cost: {e}")
        except Exception as e:
            logger.error(f"Failed to log trace to Opik: {e}")


# Cost Rates (USD)
COST_RATES = {
    # LLM Costs per 1M tokens (Input/Output)
    # Gemini 2.0 Flash is currently free in preview, but we use 1.5 Flash rates for estimation
    "gemini-2.0-flash-exp": {"input": 0.075, "output": 0.30}, 
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30}, # $/1M tokens
    
    # Audio Cost per 1000 characters
    "eleven_labs": {"char": 0.30}, # $/1000 chars (approx standard)
    
    # Image Cost per image
    "imagen": {"image": 0.04} # $/image
}

def calculate_llm_cost(model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Calculate estimated cost for LLM call."""
    # Use 1.5 Flash rates as proxy if model not found or is preview
    if "flash" in model_name and "1.5" not in model_name and model_name not in COST_RATES:
        rates = COST_RATES["gemini-1.5-flash"]
    elif model_name in COST_RATES:
        rates = COST_RATES[model_name]
    else:
        rates = COST_RATES["gemini-1.5-flash"] # Default fallback
        
    input_cost = (prompt_tokens / 1_000_000) * rates["input"]
    output_cost = (completion_tokens / 1_000_000) * rates["output"]
    return round(input_cost + output_cost, 6)

def track_cost(operation_name: str, service_name: str):
    """
    Decorator to track cost of non-LLM operations (Audio, Image).
    Usage:
        @track_cost("generate_audio", "eleven_labs")
        async def generate_audio(text, ...):
            # ...
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not OPIK_AVAILABLE:
                return await func(*args, **kwargs)
            
            tracker = OpikTracker()
            start_time = time.time()
            
            # Extract input data for cost calculation
            input_val = 0
            unit_type = "unknown"
            
            # ElevenLabs: First arg is 'text' or kwargs['text']
            # Imagen: One call = One image (usually prompt is first arg)
            if service_name == "eleven_labs":
                # Find text argument
                text = kwargs.get("text", args[0] if args else "")
                input_val = len(text)
                unit_type = "chars"
            elif service_name == "imagen":
                input_val = 1
                unit_type = "images"
            
            # Format inputs intelligently
            formatted_args = []
            for arg in args:
                formatted_args.append(str(arg)[:200])
                
            input_data = {
                "operation": operation_name,
                "service": service_name,
                "input_quantity": input_val,
                "unit": unit_type,
                "args": str(formatted_args)
            }
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                # Calculate Cost
                cost = 0.0
                if service_name == "eleven_labs":
                    # Rate is per 1000 chars
                    rate = COST_RATES["eleven_labs"]["char"]
                    cost = (input_val / 1000) * rate
                elif service_name == "imagen":
                    rate = COST_RATES["imagen"]["image"]
                    cost = input_val * rate
                
                output_data = {
                    "success": True,
                    "duration_ms": round(duration_ms, 2)
                }
                
                metadata = {
                    "estimated_cost": round(cost, 6),
                    "cost_currency": "USD",
                    "usage_unit": unit_type,
                    "usage_amount": input_val,
                    "service": service_name
                }
                
                tracker.log_trace(
                    name=operation_name,
                    input_data=input_data,
                    output_data=output_data,
                    metadata=metadata,
                    tags=["cost_tracking", service_name]
                )
                
                return result
                
            except Exception as e:
                # Log error trace
                tracker.log_trace(
                    name=operation_name,
                    input_data=input_data,
                    output_data={"error": str(e)},
                    tags=["cost_tracking", service_name, "error"]
                )
                raise e
                
        return async_wrapper
    return decorator


def track_llm_call(operation_name: str, model_name: str = "gemini-2.0-flash-exp"):
    """
    Decorator to track LLM operations with Opik.
    
    Usage:
        @track_llm_call("generate_lesson", "gemini-2.0-flash-exp")
        async def generate_lesson(...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not OPIK_AVAILABLE:
                return await func(*args, **kwargs)
            
            tracker = OpikTracker()
            start_time = time.time()
            
            # Extract relevant input data
            # Intelligently format inputs
            formatted_args = []
            for arg in args:
                if hasattr(arg, '__dict__'):
                    formatted_args.append(f"<{type(arg).__name__}>")
                elif isinstance(arg, dict):
                    # For large dicts, just show keys, for small ones show content
                    if len(str(arg)) > 500:
                        formatted_args.append(f"Dict(keys={list(arg.keys())})")
                    else:
                        formatted_args.append(str(arg))
                else:
                    formatted_args.append(str(arg))
            
            input_data = {
                "operation": operation_name,
                "model": model_name,
                "args": str(formatted_args),
                "kwargs": {k: str(v)[:200] for k, v in kwargs.items()}
            }
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                # Extract output data
                output_data = {
                    "success": True,
                    "result_type": type(result).__name__,
                    "duration_ms": round(duration_ms, 2)
                }
                
                # Capture result content
                if isinstance(result, dict):
                    # ALWAYS capture full result if it's small (like evaluation scores)
                    if len(str(result)) < 1000:
                        output_data["result"] = result
                    else:
                        output_data["result_keys"] = list(result.keys())
                        if "content" in result:
                            output_data["content_length"] = len(str(result["content"]))
                
                # Enhanced Metadata Extraction for robust monitoring
                metadata = {
                    "duration_ms": round(duration_ms, 2),
                    "success": True,
                    "model": model_name,
                    "provider": "gemini"
                }
                
                # Calculate LLM Cost if usage is available in result
                if isinstance(result, dict) and "usage" in result:
                    usage = result["usage"]
                    # Handle LiteLLM usage format (dict or object)
                    if isinstance(usage, dict):
                        prompt_tok = usage.get("prompt_tokens", 0)
                        comp_tok = usage.get("completion_tokens", 0)
                    elif hasattr(usage, "prompt_tokens"):
                        prompt_tok = usage.prompt_tokens
                        comp_tok = usage.completion_tokens
                    else:
                        prompt_tok = 0
                        comp_tok = 0
                        
                    if prompt_tok > 0:
                        cost = calculate_llm_cost(model_name, prompt_tok, comp_tok)
                        metadata["estimated_cost"] = cost
                        metadata["cost_currency"] = "USD"
                        metadata["usage"] = {
                            "prompt_tokens": prompt_tok,
                            "completion_tokens": comp_tok,
                            "total_tokens": prompt_tok + comp_tok
                        }
                
                # Extract domain-specific metadata
                if "lesson_id" in kwargs:
                    metadata["lesson_id"] = kwargs["lesson_id"]
                if "difficulty_level" in kwargs:
                    metadata["difficulty_level"] = kwargs["difficulty_level"]
                
                # Extract User Profile metadata safely
                profession = "unknown"
                if "user_profile" in kwargs:
                    profile = kwargs["user_profile"]
                    # Handle both Pydantic model and dict
                    if hasattr(profile, "profession"):
                        profession = profile.profession
                        metadata["user_profession"] = profile.profession
                        metadata["user_industry"] = getattr(profile, "industry", "unknown")
                    elif isinstance(profile, dict):
                        profession = profile.get("profession", "unknown")
                        metadata["user_profession"] = profession
                        metadata["user_industry"] = profile.get("industry", "unknown")
                elif "profession" in kwargs:
                    profession = kwargs["profession"]
                    metadata["user_profession"] = profession

                # Build Tags
                tags = ["llm", "success", operation_name, f"model:{model_name}", f"profession:{profession}"]
                
                tracker.log_trace(
                    name=operation_name,
                    input_data=input_data,
                    output_data=output_data,
                    metadata=metadata,
                    tags=tags
                )
                
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                output_data = {
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "duration_ms": round(duration_ms, 2)
                }
                
                metadata = {
                    "duration_ms": round(duration_ms, 2),
                    "success": False,
                    "error": str(e),
                    "model": model_name
                }
                
                tracker.log_trace(
                    name=operation_name,
                    input_data=input_data,
                    output_data=output_data,
                    metadata=metadata,
                    tags=["llm", "error", operation_name]
                )
                
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not OPIK_AVAILABLE:
                return func(*args, **kwargs)
            
            tracker = OpikTracker()
            start_time = time.time()
            
            # Intelligently format inputs
            formatted_args = []
            for arg in args:
                if hasattr(arg, '__dict__'):
                    formatted_args.append(f"<{type(arg).__name__}>")
                elif isinstance(arg, dict):
                    if len(str(arg)) > 500:
                        formatted_args.append(f"Dict(keys={list(arg.keys())})")
                    else:
                        formatted_args.append(str(arg))
                else:
                    formatted_args.append(str(arg))

            input_data = {
                "operation": operation_name,
                "model": model_name,
                "args": str(formatted_args),
                "kwargs": {k: str(v)[:200] for k, v in kwargs.items()}
            }
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                output_data = {
                    "success": True,
                    "result_type": type(result).__name__,
                    "duration_ms": round(duration_ms, 2)
                }

                # Capture result content
                if isinstance(result, dict):
                    if len(str(result)) < 1000:
                        output_data["result"] = result
                    else:
                        output_data["result_keys"] = list(result.keys())
                        if "content" in result:
                            output_data["content_length"] = len(str(result["content"]))
                
                metadata = {
                    "duration_ms": round(duration_ms, 2),
                    "success": True,
                    "model": model_name
                }

                # Calculate LLM Cost if usage is available in result
                if isinstance(result, dict) and "usage" in result:
                    usage = result["usage"]
                    # Handle LiteLLM usage format (dict or object)
                    if isinstance(usage, dict):
                        prompt_tok = usage.get("prompt_tokens", 0)
                        comp_tok = usage.get("completion_tokens", 0)
                    elif hasattr(usage, "prompt_tokens"):
                        prompt_tok = usage.prompt_tokens
                        comp_tok = usage.completion_tokens
                    else:
                        prompt_tok = 0
                        comp_tok = 0
                        
                    if prompt_tok > 0:
                        cost = calculate_llm_cost(model_name, prompt_tok, comp_tok)
                        metadata["estimated_cost"] = cost
                        metadata["cost_currency"] = "USD"
                        metadata["usage"] = {
                            "prompt_tokens": prompt_tok,
                            "completion_tokens": comp_tok,
                            "total_tokens": prompt_tok + comp_tok
                        }
                
                tracker.log_trace(
                    name=operation_name,
                    input_data=input_data,
                    output_data=output_data,
                    metadata=metadata,
                    tags=["llm", "success", operation_name]
                )
                
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                output_data = {
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "duration_ms": round(duration_ms, 2)
                }
                
                metadata = {
                    "duration_ms": round(duration_ms, 2),
                    "success": False,
                    "error": str(e),
                    "model": model_name
                }
                
                tracker.log_trace(
                    name=operation_name,
                    input_data=input_data,
                    output_data=output_data,
                    metadata=metadata,
                    tags=["llm", "error", operation_name]
                )
                
                raise
        
        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Initialize tracker on import
_tracker = OpikTracker()
