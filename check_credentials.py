"""
=============================================================================
FITNESS BUDDY - IBM CREDENTIAL VALIDATOR
=============================================================================
Run this script to verify your IBM watsonx.ai credentials before starting
the main application.

Usage:
    python check_credentials.py
=============================================================================
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

API_KEY    = os.environ.get("IBM_API_KEY", "")
PROJECT_ID = os.environ.get("IBM_PROJECT_ID", "")
WX_URL     = os.environ.get("IBM_WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

print("=" * 60)
print("  Fitness Buddy — IBM Credential Check")
print("=" * 60)

errors = []

# ── 1. Check values are present ──────────────────────────────────────────────
print("\n[1] Checking .env values...")

if not API_KEY or API_KEY == "your_ibm_cloud_api_key_here":
    errors.append("IBM_API_KEY is missing or still set to the placeholder value.")
    print("    ✗  IBM_API_KEY   : NOT SET")
else:
    masked = API_KEY[:6] + "..." + API_KEY[-4:]
    print(f"    ✓  IBM_API_KEY   : {masked}")

if not PROJECT_ID or PROJECT_ID == "your_watsonx_project_id_here":
    errors.append("IBM_PROJECT_ID is missing or still set to the placeholder value.")
    print("    ✗  IBM_PROJECT_ID : NOT SET")
else:
    print(f"    ✓  IBM_PROJECT_ID : {PROJECT_ID}")

print(f"    ✓  IBM_WATSONX_URL : {WX_URL}")

if errors:
    print("\n[!] Fix the above issues in your .env file first, then re-run.")
    sys.exit(1)

# ── 2. Test IAM token exchange ────────────────────────────────────────────────
print("\n[2] Testing IBM IAM token exchange...")
try:
    import requests
    resp = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": API_KEY,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=15,
    )
    if resp.status_code == 200:
        token = resp.json().get("access_token", "")
        print(f"    ✓  IAM token obtained (length={len(token)})")
    else:
        errors.append(f"IAM token exchange failed: {resp.status_code} — {resp.text[:200]}")
        print(f"    ✗  IAM token failed: {resp.status_code}")
        print(f"       Response: {resp.text[:200]}")
except Exception as e:
    errors.append(f"IAM request error: {e}")
    print(f"    ✗  Request failed: {e}")

if errors:
    print("\n[!] API key is invalid. Generate a new one at:")
    print("    https://cloud.ibm.com/iam/apikeys")
    sys.exit(1)

# ── 3. Test project access ────────────────────────────────────────────────────
print("\n[3] Testing watsonx.ai project access...")
try:
    token_resp = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": API_KEY},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=15,
    )
    bearer = token_resp.json()["access_token"]

    proj_resp = requests.get(
        f"https://api.dataplatform.cloud.ibm.com/v2/projects/{PROJECT_ID}",
        headers={"Authorization": f"Bearer {bearer}"},
        timeout=15,
    )
    if proj_resp.status_code == 200:
        name = proj_resp.json().get("entity", {}).get("name", "unknown")
        print(f"    ✓  Project found: \"{name}\"")
    elif proj_resp.status_code == 404:
        errors.append("Project not found. The PROJECT_ID does not exist in your account.")
        print(f"    ✗  Project NOT found (404). Check your IBM_PROJECT_ID.")
        print(f"       Get your Project ID at: https://dataplatform.cloud.ibm.com")
        print(f"          → Open your project → Manage → General → Project ID")
    else:
        errors.append(f"Project check returned {proj_resp.status_code}: {proj_resp.text[:200]}")
        print(f"    ✗  Unexpected response: {proj_resp.status_code}")
except Exception as e:
    errors.append(f"Project check error: {e}")
    print(f"    ✗  Request failed: {e}")

# ── 4. Test Granite model availability ───────────────────────────────────────
if not errors:
    print("\n[4] Testing Granite model generation...")
    try:
        from ibm_watsonx_ai import APIClient, Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference
        from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

        creds = Credentials(url=WX_URL, api_key=API_KEY)
        client = APIClient(creds)
        model = ModelInference(
            model_id="ibm/granite-4-h-small",
            api_client=client,
            project_id=PROJECT_ID,
            params={GenParams.MAX_NEW_TOKENS: 30},
        )
        result = model.generate_text("Say hello in one word.")
        print(f"    ✓  Granite responded: \"{result.strip()}\"")
    except Exception as e:
        errors.append(f"Granite test failed: {e}")
        print(f"    ✗  Granite test failed: {e}")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
if errors:
    print("  RESULT: ✗  Credential check FAILED")
    print("=" * 60)
    for i, err in enumerate(errors, 1):
        print(f"  {i}. {err}")
    print()
    print("  Fix guide:")
    print("  • API key  → https://cloud.ibm.com/iam/apikeys")
    print("  • Project  → https://dataplatform.cloud.ibm.com")
    print("               Open project → Manage → General → copy Project ID")
    sys.exit(1)
else:
    print("  RESULT: ✓  All checks passed! Run: python app.py")
    print("=" * 60)
