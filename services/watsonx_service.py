"""
=============================================================================
FITNESS BUDDY - IBM watsonx.ai SERVICE
=============================================================================
Thin wrapper around ibm-watsonx-ai SDK that exposes a single generate()
call used by every agent in the system.
"""

import os
try:
    # ibm-watsonx-ai >= 1.3 layout
    from ibm_watsonx_ai import APIClient, Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
except ImportError:
    # Fallback for older SDK layouts
    from ibm_watson_machine_learning import APIClient, Credentials          # type: ignore
    from ibm_watson_machine_learning.foundation_models import ModelInference # type: ignore
    from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams  # type: ignore
from config import Config

_client: APIClient | None = None
_model: ModelInference | None = None


def _get_model() -> ModelInference:
    """Lazily initialise and return the shared Granite model instance."""
    global _client, _model
    if _model is not None:
        return _model

    if not Config.IBM_API_KEY or not Config.IBM_PROJECT_ID:
        raise RuntimeError(
            "IBM_API_KEY and IBM_PROJECT_ID must be set in the .env file."
        )

    credentials = Credentials(
        url=Config.IBM_WATSONX_URL,
        api_key=Config.IBM_API_KEY,
    )
    _client = APIClient(credentials)
    _model = ModelInference(
        model_id=Config.GRANITE_MODEL_ID,
        api_client=_client,
        project_id=Config.IBM_PROJECT_ID,
        params={
            GenParams.MAX_NEW_TOKENS: 1024,
            GenParams.TEMPERATURE: 0.7,
            GenParams.TOP_P: 0.9,
            GenParams.REPETITION_PENALTY: 1.1,
        },
    )
    return _model


def generate(prompt: str, max_tokens: int = 1024) -> str:
    """
    Send *prompt* to Granite and return the generated text.

    Falls back to a descriptive error string so the UI still renders.
    """
    try:
        model = _get_model()
        response = model.generate_text(
            prompt=prompt,
            params={GenParams.MAX_NEW_TOKENS: max_tokens},
        )
        return response.strip() if isinstance(response, str) else str(response).strip()
    except Exception as exc:
        return (
            f"⚠️ AI service temporarily unavailable. "
            f"Please check your IBM credentials in the .env file. "
            f"Error: {exc}"
        )
