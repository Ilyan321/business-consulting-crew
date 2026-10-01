import os
from typing import Optional, Dict, Any, List
from datetime import datetime

_supabase_client = None


def get_supabase_client():
    """
    Returns an authenticated Supabase client if SUPABASE_URL and SUPABASE_KEY
    are provided in Streamlit secrets or environment variables.
    """
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    supabase_url = ""
    supabase_key = ""

    # 1. Try Streamlit secrets
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            supabase_url = st.secrets.get("SUPABASE_URL", "")
            supabase_key = st.secrets.get("SUPABASE_KEY", "") or st.secrets.get("SUPABASE_ANON_KEY", "")
    except Exception:
        pass

    # 2. Try environment variables
    if not supabase_url:
        supabase_url = os.environ.get("SUPABASE_URL", "")
    if not supabase_key:
        supabase_key = os.environ.get("SUPABASE_KEY", "") or os.environ.get("SUPABASE_ANON_KEY", "")

    if supabase_url and supabase_key:
        try:
            from supabase import create_client
            _supabase_client = create_client(supabase_url.strip(), supabase_key.strip())
            return _supabase_client
        except Exception as e:
            print(f"Failed to initialize Supabase client: {e}")
            return None

    return None


def is_supabase_configured() -> bool:
    """Checks whether Supabase credentials are available and valid."""
    return get_supabase_client() is not None


def save_report_to_supabase(
    business_idea: str,
    target_industry: str,
    target_market: str,
    budget_or_stage: str,
    strategic_focus: str,
    final_report: str,
    step_outputs: List[Dict[str, Any]],
    model: str,
    elapsed_time: float,
) -> Dict[str, Any]:
    """
    Saves a generated business consulting report to the Supabase 'consulting_reports' table.
    """
    client = get_supabase_client()
    if not client:
        return {"success": False, "error": "Supabase is not configured in secrets."}

    payload = {
        "business_idea": business_idea,
        "target_industry": target_industry,
        "target_market": target_market,
        "budget_or_stage": budget_or_stage,
        "strategic_focus": strategic_focus,
        "final_report": final_report,
        "step_outputs": step_outputs,
        "model_used": model,
        "elapsed_time": elapsed_time,
        "created_at": datetime.utcnow().isoformat(),
    }

    try:
        response = client.table("consulting_reports").insert(payload).execute()
        return {"success": True, "data": response.data}
    except Exception as e:
        return {"success": False, "error": str(e)}


def fetch_reports_from_supabase(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Retrieves the most recent consulting reports from Supabase.
    """
    client = get_supabase_client()
    if not client:
        return []

    try:
        response = (
            client.table("consulting_reports")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data or []
    except Exception as e:
        print(f"Error fetching reports from Supabase: {e}")
        return []
