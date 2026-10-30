"""Public UI for CivicAccess."""

from __future__ import annotations


def render_public_lookup_page() -> str:
    """Render the accessible public-facing CivicAccess review page."""

    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CivicAccess Public Accessibility Support</title>
<style>
  :root { --ink:#17202a; --muted:#56606a; --paper:#fffdf7; --blue:#175b83; --green:#2f6b50; --gold:#d8b45b; --line:#d7c8a8; --danger:#9a3d2f; }
  * { box-sizing: border-box; }
  body { margin:0; color:var(--ink); font-family:"Aptos","Segoe UI",sans-serif; background:#f7f1e6; }
  .skip-link { position:absolute; left:1rem; top:-4rem; background:var(--ink); color:white; padding:.7rem 1rem; border-radius:4px; z-index:10; }
  .skip-link:focus { top:1rem; }
  header, main, footer { width:min(1120px, calc(100% - 32px)); margin:0 auto; }
  header { padding:44px 0 22px; }
  .eyebrow { color:var(--blue); text-transform:uppercase; font-weight:800; font-size:.8rem; }
  h1 { max-width:920px; margin:0; font-family:Georgia,"Times New Roman",serif; font-size:clamp(2.4rem,7vw,4.8rem); line-height:1; }
  .lede { max-width:820px; font-size:clamp(1.05rem,2.2vw,1.35rem); line-height:1.55; color:#31404a; }
  .badge { display:inline-block; padding:.45rem .75rem; border-radius:4px; background:var(--green); color:white; font-weight:900; }
  .grid { display:grid; grid-template-columns:repeat(12,1fr); gap:16px; }
  .panel { grid-column:span 6; min-width:0; padding:22px; border:1px solid var(--line); border-radius:8px; background:rgba(255,253,247,.94); }
  .panel.large { grid-column:span 12; }
  h2,h3 { font-family:Georgia,"Times New Roman",serif; }
  h2 { margin:0 0 14px; font-size:clamp(1.45rem,3vw,2.3rem); }
  p, li { line-height:1.6; }
  label { display:block; margin:.8rem 0 .35rem; font-weight:800; }
  textarea, input, select, button { width:100%; border:1px solid #9fb0b8; border-radius:6px; padding:.8rem 1rem; font:inherit; }
  textarea, input, select { background:#f3f7f8; color:var(--ink); }
  button { width:fit-content; min-width:180px; margin-top:1rem; border:0; background:var(--blue); color:white; font-weight:900; cursor:pointer; }
  button:hover { background:#104462; }
  button:disabled { background:#6d7b83; cursor:not-allowed; }
  .result { margin-top:18px; padding:16px; border-left:6px solid var(--green); border-radius:6px; background:white; }
  .result.warning { border-left-color:var(--danger); background:#fff8f4; }
  .result.pending { border-left-color:var(--gold); }
  .kicker { color:var(--muted); font-size:.86rem; font-weight:900; text-transform:uppercase; }
  .notice { margin:24px 0 0; padding:18px; border:1px dashed var(--danger); border-radius:8px; background:rgba(154,61,47,.10); }
  .stack { display:grid; gap:12px; }
  footer { padding:38px 0 56px; color:var(--muted); }
  :focus-visible { outline:4px solid var(--gold); outline-offset:3px; }
  @media (max-width:760px) { header{padding-top:34px}.panel{grid-column:span 12;padding:18px}button{width:100%} }
</style>
</head>
<body>
<a class="skip-link" href="#main">Skip to main content</a>
<header>
  <p class="eyebrow">CivicSuite / CivicAccess</p>
  <h1>Make public information easier to read, reach, and preserve.</h1>
  <p class="lede">CivicAccess gives staff a deterministic review path for accessible forms, public notices, plain-language rewrites, multilingual samples, ADA Title II review support, tagged-PDF expectations, and municipal-record exports.</p>
  <p><span class="badge">v0.4.0 standalone readiness candidate</span></p>
</header>
<main id="main" tabindex="-1">
  <section class="grid" aria-labelledby="review-title">
    <article class="panel large">
      <p class="kicker">Accessibility review</p>
      <h2 id="review-title">Public notice check</h2>
      <label for="title">Notice title</label>
      <input id="title" value="Water shutoff notice">
      <label for="notice">Notice text</label>
      <textarea id="notice" rows="5">Pursuant to municipal code, residents must remit payment prior to the deadline.</textarea>
      <label><input id="altText" type="checkbox" style="width:auto"> Images already have alt text</label>
      <button id="runReview" type="button">Run review</button>
      <div id="reviewResult" class="result pending" role="status" aria-live="polite">
        <h3>Partial review pending</h3>
        <p>Add or confirm the notice fields, then run the review. CivicAccess will show actionable fixes before staff publication review.</p>
      </div>
    </article>
    <article class="panel">
      <p class="kicker">Accessible forms</p>
      <h2>Form publication plan</h2>
      <div class="result"><p>Required fields: name, contact, and request. Errors must stay next to the field they describe.</p></div>
    </article>
    <article class="panel">
      <p class="kicker">Plain language</p>
      <h2>Replace jargon</h2>
      <div class="result"><p><strong>Before:</strong> remit payment prior to the deadline.</p><p><strong>After:</strong> pay before the deadline.</p></div>
    </article>
    <article class="panel">
      <p class="kicker">Multilingual support</p>
      <h2>Human-reviewed variants</h2>
      <div class="result"><p>Spanish and Vietnamese samples are marked as draft variants that need qualified human review before publication.</p></div>
    </article>
    <article class="panel">
      <p class="kicker">Tagged PDF</p>
      <h2>Heading expectations</h2>
      <div class="result"><p>PDF packages must start with one H1, keep heading levels in order, and verify tags before publication.</p></div>
    </article>
    <article class="panel">
      <p class="kicker">Records export</p>
      <h2>Keep provenance</h2>
      <div class="result"><p>Exports preserve source text, rewritten text, reviewer, checklist, and publication context for records requests.</p></div>
    </article>
    <article class="panel">
      <p class="kicker">ADA boundary</p>
      <h2>Support, not certification</h2>
      <div class="result warning"><p>CivicAccess does not provide legal advice, certified ADA compliance, official translation certification, or final publication approval. ADA coordinators and qualified reviewers remain responsible for official decisions.</p></div>
    </article>
  </section>
  <section class="notice" aria-labelledby="boundary-title">
    <h2 id="boundary-title">Publication boundary</h2>
    <p>Every output is advisory support. Staff must review fixes, translation drafts, ADA Title II notes, and export packages before publication.</p>
  </section>
</main>
<footer><p>CivicAccess is part of the Apache 2.0 CivicSuite open-source municipal AI project.</p></footer>
<script>
  const result = document.getElementById("reviewResult");
  const title = document.getElementById("title");
  const notice = document.getElementById("notice");
  const altText = document.getElementById("altText");
  const runReview = document.getElementById("runReview");
  const initialParams = new URLSearchParams(window.location.search);
  if (initialParams.has("title")) title.value = initialParams.get("title");
  if (initialParams.has("notice")) notice.value = initialParams.get("notice");
  if (initialParams.get("alt") === "1") altText.checked = true;

  function appendText(tagName, text) {
    const node = document.createElement(tagName);
    node.textContent = text;
    result.appendChild(node);
    return node;
  }

  function setResult(kind, heading, body, items) {
    result.className = "result" + (kind ? " " + kind : "");
    result.replaceChildren();
    appendText("h3", heading);
    appendText("p", body);
    if (items && items.length) {
      const list = document.createElement("ul");
      for (const item of items) {
        const listItem = document.createElement("li");
        listItem.textContent = item;
        list.appendChild(listItem);
      }
      result.appendChild(list);
    }
  }

  runReview.addEventListener("click", async () => {
    setResult("pending", "Loading review", "Checking the notice text and publication fields.", []);
    runReview.disabled = true;
    try {
      const response = await fetch("/api/v1/civicaccess/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: title.value,
          body: notice.value,
          has_alt_text: altText.checked,
          language: "en",
        }),
      });
      const payload = await response.json();
      if (!response.ok) {
        const detail = payload.detail || {};
        throw new Error([detail.message, detail.fix].filter(Boolean).join(" "));
      }
      const fixes = (payload.findings || []).map((finding) => finding.fix);
      if (payload.status === "passes-sample-checks") {
        setResult("", "Sample checks passed", "Staff review is still required before publication.", payload.next_steps || []);
      } else if (fixes.length) {
        setResult("warning", "Needs fixes", "Resolve these items before staff publication approval.", fixes);
      } else {
        setResult("warning", "Review needs staff attention", payload.disclaimer || "Staff review is required before publication.", []);
      }
    } catch (error) {
      setResult("warning", "Review could not finish", error.message || "Check that the notice text is present, then run the review again. If this happens in the installed stack, staff should check the CivicAccess service health endpoint.", []);
    } finally {
      runReview.disabled = false;
    }
  });
</script>
</body>
</html>
"""


def render_staff_page() -> str:
    """Render the staff review workspace for saved CivicAccess work.

    The page never embeds the server write token. Staff paste it into a field; it is kept in
    sessionStorage and sent as the X-CivicAccess-Write-Token header on save/export only.
    """

    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CivicAccess Staff Workspace</title>
<style>
  :root { --ink:#17202a; --muted:#56606a; --paper:#fffdf7; --blue:#175b83; --green:#2f6b50; --gold:#d8b45b; --line:#d7c8a8; --danger:#9a3d2f; }
  * { box-sizing: border-box; }
  body { margin:0; color:var(--ink); font-family:"Aptos","Segoe UI",sans-serif; background:#f7f1e6; }
  .skip-link { position:absolute; left:1rem; top:-4rem; background:var(--ink); color:white; padding:.7rem 1rem; border-radius:4px; z-index:10; }
  .skip-link:focus { top:1rem; }
  header, main, footer { width:min(1180px, calc(100% - 32px)); margin:0 auto; }
  header { padding:34px 0 18px; }
  .eyebrow { color:var(--blue); text-transform:uppercase; font-weight:800; font-size:.8rem; }
  h1 { margin:0; font-family:Georgia,"Times New Roman",serif; font-size:clamp(2rem,5vw,3.8rem); line-height:1; }
  .lede { max-width:860px; font-size:1.12rem; line-height:1.55; color:#31404a; }
  .grid { display:grid; grid-template-columns:repeat(12,1fr); gap:16px; }
  .panel { grid-column:span 6; min-width:0; padding:20px; border:1px solid var(--line); border-radius:8px; background:rgba(255,253,247,.96); }
  .panel.large { grid-column:span 12; }
  h2,h3 { font-family:Georgia,"Times New Roman",serif; }
  h2 { margin:0 0 12px; font-size:1.75rem; }
  p, li { line-height:1.6; }
  label { display:block; margin:.8rem 0 .35rem; font-weight:800; }
  textarea, input, select, button { width:100%; border:1px solid #9fb0b8; border-radius:6px; padding:.8rem 1rem; font:inherit; }
  textarea, input, select { background:#f3f7f8; color:var(--ink); }
  button { width:fit-content; min-width:180px; margin-top:1rem; border:0; background:var(--blue); color:white; font-weight:900; cursor:pointer; }
  button:hover { background:#104462; }
  button:disabled { background:#6d7b83; cursor:not-allowed; }
  .result { margin-top:14px; padding:14px; border-left:6px solid var(--green); border-radius:6px; background:white; }
  .warning { border-left-color:var(--danger); background:#fff8f4; }
  .muted { color:var(--muted); }
  .review-list { display:grid; gap:10px; }
  .review-card { border:1px solid var(--line); border-radius:6px; padding:12px; background:white; }
  .review-card button { min-width:140px; }
  footer { padding:34px 0 52px; color:var(--muted); }
  :focus-visible { outline:4px solid var(--gold); outline-offset:3px; }
  @media (max-width:760px) { .panel{grid-column:span 12;padding:18px}button{width:100%} }
</style>
</head>
<body>
<a class="skip-link" href="#main">Skip to main content</a>
<header>
  <p class="eyebrow">CivicSuite / CivicAccess staff</p>
  <h1>Review, preserve, and export accessible publication work.</h1>
  <p class="lede">This workspace gives staff a saved local queue for accessibility reviews, records-ready exports, and downstream publication contracts used by other CivicSuite modules.</p>
</header>
<main id="main" tabindex="-1">
  <section class="grid" aria-labelledby="new-review-title">
    <article class="panel">
      <h2 id="new-review-title">Create saved review</h2>
      <label for="title">Publication title</label>
      <input id="title" value="Public meeting notice">
      <label for="body">Publication text</label>
      <textarea id="body" rows="6">Residents may request an accommodation before the meeting.</textarea>
      <label><input id="altText" type="checkbox" style="width:auto"> Images already have alt text</label>
      <label for="writeToken">Staff write token</label>
      <input id="writeToken" type="password" autocomplete="off" placeholder="Paste the CivicAccess write token to save or export">
      <button id="createReview" type="button">Save review</button>
      <div id="createStatus" class="result" role="status" aria-live="polite">
        <p>Saving and exporting require the staff write token. Paste it above; it stays in this browser session only.</p>
      </div>
    </article>
    <article class="panel">
      <h2>System readiness</h2>
      <div id="readiness" class="result" role="status" aria-live="polite"><p>Loading readiness...</p></div>
      <h2>Downstream contracts</h2>
      <div id="contracts" class="result" role="status" aria-live="polite"><p>Loading integration contracts...</p></div>
    </article>
    <article class="panel large">
      <h2>Saved review queue</h2>
      <div id="reviews" class="review-list" role="status" aria-live="polite"><p>Loading saved reviews...</p></div>
      <div id="exportResult" class="result" role="status" aria-live="polite"><p>Select a saved review to export a records-ready package.</p></div>
    </article>
  </section>
</main>
<footer><p>CivicAccess staff outputs are advisory. Staff approval, qualified translation review, and ADA coordinator review remain required for official publication decisions.</p></footer>
<script>
  const title = document.getElementById("title");
  const body = document.getElementById("body");
  const altText = document.getElementById("altText");
  const writeToken = document.getElementById("writeToken");
  const createReview = document.getElementById("createReview");
  const createStatus = document.getElementById("createStatus");

  const savedToken = sessionStorage.getItem("civicaccessWriteToken");
  if (savedToken) writeToken.value = savedToken;
  function currentToken() {
    const value = writeToken.value.trim();
    if (value) sessionStorage.setItem("civicaccessWriteToken", value);
    return value;
  }
  const readiness = document.getElementById("readiness");
  const contracts = document.getElementById("contracts");
  const reviews = document.getElementById("reviews");
  const exportResult = document.getElementById("exportResult");

  function replaceWithText(node, heading, text, warning=false) {
    node.className = "result" + (warning ? " warning" : "");
    node.replaceChildren();
    const h = document.createElement("h3");
    h.textContent = heading;
    const p = document.createElement("p");
    p.textContent = text;
    node.append(h, p);
  }

  async function loadReadiness() {
    const payload = await (await fetch("/api/v1/civicaccess/readiness")).json();
    replaceWithText(readiness, payload.ready ? "Ready" : "Needs setup", payload.ready ? `Review database ready. Saved reviews: ${payload.review_count}.` : (payload.blockers || []).join(" "), !payload.ready);
  }

  async function loadContracts() {
    const payload = await (await fetch("/api/v1/civicaccess/integration-contracts")).json();
    const names = (payload.provides || []).map((item) => item.contract).join(", ");
    replaceWithText(contracts, "Contracts published", names || "No contracts published.", false);
  }

  async function loadReviews() {
    const payload = await (await fetch("/api/v1/civicaccess/reviews")).json();
    reviews.replaceChildren();
    if (!payload.reviews || payload.reviews.length === 0) {
      const empty = document.createElement("p");
      empty.className = "muted";
      empty.textContent = "No saved reviews yet.";
      reviews.appendChild(empty);
      return;
    }
    for (const review of payload.reviews) {
      const card = document.createElement("article");
      card.className = "review-card";
      const heading = document.createElement("h3");
      heading.textContent = review.title || "Untitled publication";
      const summary = document.createElement("p");
      summary.textContent = `${review.status}; ${review.finding_count} finding(s); ${review.language}`;
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = "Export for records";
      button.addEventListener("click", () => exportReview(review.review_id));
      card.append(heading, summary, button);
      reviews.appendChild(card);
    }
  }

  async function exportReview(reviewId) {
    const response = await fetch(`/api/v1/civicaccess/reviews/${reviewId}/records-export`, {
      method: "POST",
      headers: { "X-CivicAccess-Write-Token": currentToken() },
    });
    const payload = await response.json();
    if (!response.ok) {
      replaceWithText(exportResult, "Records export unavailable", payload.detail?.message || "Staff write token is missing or invalid.", true);
      return;
    }
    replaceWithText(exportResult, "Records export ready", `${payload.target_module}: ${payload.export.status}. ${payload.export.retention_note}`);
  }

  createReview.addEventListener("click", async () => {
    createReview.disabled = true;
    try {
      const response = await fetch("/api/v1/civicaccess/review", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CivicAccess-Write-Token": currentToken(),
        },
        body: JSON.stringify({ title: title.value, body: body.value, has_alt_text: altText.checked, language: "en" }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail?.message || "Review failed.");
      replaceWithText(createStatus, "Review saved", `${payload.review_id}: ${payload.status}`);
      await Promise.all([loadReadiness(), loadReviews()]);
    } catch (error) {
      replaceWithText(createStatus, "Review could not be saved", error.message || "Check service health and try again.", true);
    } finally {
      createReview.disabled = false;
    }
  });

  Promise.all([loadReadiness(), loadContracts(), loadReviews()]).catch((error) => {
    replaceWithText(readiness, "Workspace could not load", error.message || "Check CivicAccess service health.", true);
  });
</script>
</body>
</html>
"""
