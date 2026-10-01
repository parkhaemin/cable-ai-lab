const state = { productId: null, pipeline: "rag" };
const list = document.querySelector("#productList");
const result = document.querySelector("#result");
const process = document.querySelector("#process");
const question = document.querySelector("#question");
const askButton = document.querySelector("#askButton");
const mobileSearch = document.querySelector("#mobileSearch");
const mobileQuestion = document.querySelector("#mobileQuestion");
const mobileAskButton = document.querySelector("#mobileAskButton");

function el(tag, className, value) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (value !== undefined) node.textContent = value;
  return node;
}

async function getJSON(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error("서버 응답을 확인해 주세요.");
  return response.json();
}

async function boot() {
  try {
    const [status, products] = await Promise.all([getJSON("/api/status"), getJSON("/api/products")]);
    const badge = document.querySelector("#modeBadge");
    badge.textContent = status.mode === "live" ? "LIVE / OPENAI + PGVECTOR" : "DEMO / LOCAL";
    badge.classList.toggle("live", status.mode === "live");
    products.forEach((product, index) => {
      const button = el("button", "product");
      button.type = "button";
      button.setAttribute("aria-pressed", "false");
      button.append(el("span", "num", `0${index + 1} / ${product.category}`));
      button.append(el("strong", "", product.name));
      button.append(el("span", "meta", `${product.color.toUpperCase()} · ${product.price.toLocaleString()}원 (예시)`));
      button.addEventListener("click", () => {
        state.productId = state.productId === product.id ? null : product.id;
        document.querySelector("#mobileProductLabel").textContent =
          state.productId ? `${product.name} 선택됨` : "상품 선택 없이 질문";
        document.querySelectorAll(".product").forEach((item) => {
          const selected = item === button && state.productId === product.id;
          item.classList.toggle("selected", selected);
          item.setAttribute("aria-pressed", String(selected));
        });
      });
      list.append(button);
    });
  } catch (error) {
    list.append(el("p", "error", `상품을 불러오지 못했습니다: ${error.message}`));
  }
}

function setPipeline(value) {
  state.pipeline = value;
  document.querySelector("#mobilePipelineLabel").textContent =
    value === "rag" ? "RAG · 문서 근거" : "AGENT · 도구 호출";
  document.querySelectorAll(".segment").forEach((button) => {
    const active = button.dataset.pipeline === value;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", String(active));
  });
}

function renderAnswer(data) {
  result.replaceChildren();
  result.append(el("span", "result-overline", `${data.mode.toUpperCase()} / ${data.generated ? "MODEL GENERATED" : "RULE-BASED OUTPUT"}`));
  result.append(el("h4", "", state.pipeline === "rag" ? "Evidence → Answer" : "Tools → Answer"));
  result.append(el("p", "answer-text", data.answer));
  process.replaceChildren();
  if (state.pipeline === "rag") {
    const hits = data.retrieval || [];
    if (!hits.length) process.append(el("p", "process-empty", "검색 결과가 없습니다."));
    hits.forEach((hit, index) => {
      const card = el("article", "evidence");
      const title = el("div", "evidence-header");
      title.append(el("span", "", `0${index + 1} / ${hit.title} [${hit.id}]`));
      title.append(el("span", "tag", `SIMILARITY ${hit.score.toFixed(3)}`));
      card.append(title, el("p", "", hit.content));
      process.append(card);
    });
  } else {
    const trace = data.tool_trace || [];
    if (!trace.length) process.append(el("p", "process-empty", "모델이 도구를 호출하지 않았습니다."));
    trace.forEach((step, index) => {
      const card = el("article", "evidence");
      card.append(el("div", "evidence-header", `0${index + 1} / ${step.tool}`));
      card.append(el("pre", "trace-pre", `입력 ${JSON.stringify(step.input, null, 2)}\n출력 ${JSON.stringify(step.output, null, 2)}`));
      process.append(card);
    });
  }
}

async function ask(fromMobile = false) {
  if (question.value.trim().length < 2) {
    (fromMobile ? mobileQuestion : question).focus();
    return;
  }
  askButton.disabled = true;
  mobileAskButton.disabled = true;
  askButton.textContent = "답변을 준비하고 있습니다…";
  mobileAskButton.textContent = "검색 중…";
  try {
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({question: question.value.trim(), pipeline: state.pipeline, product_id: state.productId})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "서버 오류");
    renderAnswer(data);
    if (fromMobile) {
      result.scrollIntoView({
        behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth",
        block: "center"
      });
    }
  } catch (error) {
    result.replaceChildren(el("span", "result-overline", "REQUEST ERROR"), el("p", "error", error.message));
    process.replaceChildren();
    if (fromMobile) result.scrollIntoView({block: "center"});
  } finally {
    askButton.disabled = false;
    mobileAskButton.disabled = false;
    askButton.replaceChildren(document.createTextNode("질문 실행하기 "), el("span", "", "↗"));
    mobileAskButton.replaceChildren(document.createTextNode("질문하기 "), el("span", "", "↗"));
  }
}

document.querySelectorAll(".segment").forEach(button => button.addEventListener("click", () => setPipeline(button.dataset.pipeline)));
document.querySelectorAll(".suggestions button").forEach(button => button.addEventListener("click", () => {
  question.value = button.dataset.question;
  mobileQuestion.value = question.value;
  setPipeline(button.dataset.method);
  (window.matchMedia("(max-width: 650px)").matches ? mobileQuestion : question).focus();
}));
question.addEventListener("input", () => { mobileQuestion.value = question.value; });
mobileQuestion.addEventListener("input", () => { question.value = mobileQuestion.value; });
askButton.addEventListener("click", () => ask(false));
mobileSearch.addEventListener("submit", (event) => {
  event.preventDefault();
  question.value = mobileQuestion.value;
  mobileQuestion.blur();
  ask(true);
});
boot();
