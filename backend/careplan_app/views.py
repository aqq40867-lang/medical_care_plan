import json
import uuid
import os
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# ============================================
# "数据库"：就是一个 Python 字典，存在内存里
# 重启服务器数据就没了 —— Day 2 故意留的缺陷
# ============================================
ORDERS = {}

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"


def build_prompt(data):
    """把表单数据拼成发给 LLM 的 prompt"""
    return f"""You are a clinical pharmacist. Based on the following patient
information, generate a care plan.

Patient Name: {data.get('patient_name')}
Medication: {data.get('medication_name')}
Primary Diagnosis: {data.get('diagnosis')}
Referring Provider: {data.get('provider_name')}
Patient Records: {data.get('patient_records')}

The care plan MUST include exactly these four sections:
1. Problem list
2. Goals
3. Pharmacist interventions
4. Monitoring plan
"""


@csrf_exempt
def create_order(request):
    """
    POST /api/orders/
    同步调用：会卡住直到 DeepSeek 返回结果
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    data = json.loads(request.body)
    order_id = str(uuid.uuid4())[:8]

    ORDERS[order_id] = {
        "id": order_id,
        "status": "processing",
        "patient_name": data.get("patient_name"),
        "medication_name": data.get("medication_name"),
        "care_plan": None,
    }

    try:
        prompt = build_prompt(data)
        response = requests.post(
            DEEPSEEK_URL,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
            timeout=60,
        )
        response.raise_for_status()
        result = response.json()
        care_plan_text = result["choices"][0]["message"]["content"]

        ORDERS[order_id]["care_plan"] = care_plan_text
        ORDERS[order_id]["status"] = "completed"

    except Exception as e:
        print("LLM call failed:", e)  # 先简单打印方便调试
        ORDERS[order_id]["status"] = "failed"

    return JsonResponse(ORDERS[order_id])


def get_order(request, order_id):
    """GET /api/orders/<order_id>/ —— 查一个订单的状态和内容"""
    order = ORDERS.get(order_id)
    if not order:
        return JsonResponse({"error": "Order not found"}, status=404)
    return JsonResponse(order)