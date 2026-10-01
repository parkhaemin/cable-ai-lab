"""Two read-only tools. Live mode lets an LLM select calls; demo uses fixed rules."""
import json
import re
from .config import live_settings
from .data import load_products, product_by_id

TOOLS = [
    {"type":"function","name":"search_products",
     "description":"상품 이름, 색상, 카테고리로 학습용 상품 목록을 검색합니다.",
     "strict":True,
     "parameters":{"type":"object","properties":{"query":{"type":"string"}},
                   "required":["query"],"additionalProperties":False}},
    {"type":"function","name":"calculate_total",
     "description":"상품 id와 수량으로 예시 상품의 총액을 계산합니다. 결제는 수행하지 않습니다.",
     "strict":True,
     "parameters":{"type":"object","properties":{
         "product_id":{"type":"string"},
         "quantity":{"type":"integer"}},
         "required":["product_id","quantity"],"additionalProperties":False}},
]


def search_products(query: str) -> list[dict]:
    # If an id or exact name appears, prefer that product.
    words = [w.casefold() for w in re.findall(r"[A-Za-z0-9가-힣]+", query)
             if w.casefold() not in {"cable", "tee", "pants", "상품", "추천", "가격", "몇", "개"}]
    products = load_products()
    exact = [p for p in products if p["id"].casefold() in words or p["name"].casefold() in query.casefold()]
    if exact:
        return exact
    if not words:
        return products
    return [p for p in products if any(
        w in (p["name"] + " " + p["category"] + " " + p["color"] + " " + p["description"]).casefold()
        for w in words
    )]


def calculate_total(product_id: str, quantity: int) -> dict:
    if type(quantity) is not int or not 1 <= quantity <= 50:
        return {"error":"수량은 1~50의 정수여야 합니다."}
    product = product_by_id(product_id)
    if product is None:
        return {"error":"해당 상품 id가 없습니다."}
    if quantity > product["stock"]:
        return {"error":"예시 재고보다 수량이 많습니다.","stock":product["stock"]}
    return {"product_id":product_id,"name":product["name"],
            "quantity":quantity,"unit_price":product["price"],
            "total":product["price"] * quantity,"currency":"KRW",
            "notice":"학습용 예시 가격·재고이며 실제 주문이 아닙니다."}


def _execute(name: str, args: dict):
    if name == "search_products":
        return search_products(str(args["query"]))
    if name == "calculate_total":
        return calculate_total(str(args["product_id"]), args["quantity"])
    return {"error":"허용되지 않은 도구입니다."}


def agent_demo(question: str) -> dict:
    products = search_products(question)
    trace = [{"tool":"search_products","input":{"query":question},"output":products}]
    qty = re.search(r"(\d+)\s*개", question)
    if qty and len(products) == 1 and any(w in question for w in ("가격", "합계", "총액", "얼마")):
        result = calculate_total(products[0]["id"], int(qty.group(1)))
        trace.append({"tool":"calculate_total",
                      "input":{"product_id":products[0]["id"],"quantity":int(qty.group(1))},
                      "output":result})
        answer = (f'{result["name"]} {result["quantity"]}개 예시 합계는 {result["total"]:,}원입니다.'
                  if "total" in result else result["error"])
    elif products:
        answer = "찾은 예시 상품: " + ", ".join(f'{p["name"]} ({p["price"]:,}원)' for p in products)
    else:
        answer = "일치하는 예시 상품을 찾지 못했습니다."
    return {"answer":answer,"tool_trace":trace,"mode":"demo","generated":False}


def agent_live(question: str) -> dict:
    from openai import OpenAI
    key, model, _, _ = live_settings()
    client = OpenAI(api_key=key)
    instructions = ("한국어로 답하세요. 상품 정보·가격·재고는 반드시 제공된 도구의 결과만 사용하세요. "
                    "도구는 읽기 전용이며 구매·결제는 할 수 없습니다. 모르면 모른다고 답하세요.")
    messages = [{"role":"user","content":question}]
    trace = []
    for _ in range(3):
        response = client.responses.create(model=model, instructions=instructions,
                                           input=messages, tools=TOOLS, max_output_tokens=350)
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            return {"answer":response.output_text.strip() or "답변을 생성하지 못했습니다.",
                    "tool_trace":trace,"mode":"live","generated":True}
        messages.extend(response.output)
        for call in calls:
            args = {}
            try:
                args = json.loads(call.arguments)
                result = _execute(call.name, args)
            except (ValueError, KeyError, TypeError) as exc:
                result = {"error":f"도구 입력 오류: {type(exc).__name__}"}
            trace.append({"tool":call.name,"input":args if isinstance(args, dict) else {},
                          "output":result})
            messages.append({"type":"function_call_output","call_id":call.call_id,
                             "output":json.dumps(result, ensure_ascii=False)})
    return {"answer":"도구 호출 횟수 제한에 도달했습니다. 질문을 간단히 바꿔 주세요.",
            "tool_trace":trace,"mode":"live","generated":False}


def run_agent(question: str, run_mode: str = "demo") -> dict:
    return agent_demo(question) if run_mode == "demo" else agent_live(question)
