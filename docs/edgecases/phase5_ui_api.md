# Phase 5 Edge Cases: UI & API Layer

> **Scope:** Minimal Web Interface, FastAPI Endpoints, Input Validation, UI Responsiveness, and Frontend Security.

---

## 1. Overview of Phase 5 Risks

Phase 5 delivers the minimal frontend and API layer. The UI must prominently exhibit the required compliance disclaimer (*"Facts-only. No investment advice."*), 3 sample quick-prompts, and provide a resilient, responsive interface against malicious payloads, latency spikes, or rendering failures.

---

## 2. Detailed Edge Cases & Failure Modes

### Edge Case 5.1: XSS (Cross-Site Scripting) & Markdown Injection
- **Scenario:** An adversary submits a query containing HTML/JavaScript injection:
  `<script>alert('xss')</script>` or `<img src=x onerror=stealToken()>`.
- **Failure Mode:** If the chat interface renders raw HTML or improperly parses markdown, user scripts execute in the browser.
- **Detection:** Presence of `<script>`, `onerror`, `onload`, or raw HTML tags in query text or rendered response.
- **Mitigation Strategy:**
  - Sanitize all rendered user inputs and bot outputs using a secure markdown renderer (e.g., `DOMPurify` or safe markdown parsers that escape unwhitelisted HTML tags).
  - Enforce Content Security Policy (CSP) headers in the FastAPI server.

---

### Edge Case 5.2: Excessive Payload Size / Prompt Flooding
- **Scenario:** A user or bot pastes an entire financial report or a 20,000-character wall of text into the input field.
- **Failure Mode:** Memory exhaustion in the server, excessive token usage, high API costs, or connection timeouts.
- **Detection:** Query character length $> 500$ characters.
- **Mitigation Strategy:**
  - Impose frontend character limit (`maxlength="300"`) on the input textarea with a live counter.
  - Enforce backend validation in FastAPI (`Pydantic` schema validating `len(query) <= 300` characters); return HTTP 422 if exceeded.

---

### Edge Case 5.3: Rapid Double Submissions & Debounce Failures
- **Scenario:** A user clicks the "Send" button multiple times rapidly or clicks a sample question pill repeatedly while a query is in-flight.
- **Failure Mode:** Parallel duplicate requests trigger multiple concurrent LLM calls, corrupting chat state or causing race conditions.
- **Detection:** Multiple requests received from the same client session within $<500$ ms.
- **Mitigation Strategy:**
  - Disable the submit button and quick-action pills immediately upon click.
  - Display an animated loading indicator until the response stream or JSON is received.
  - Implement frontend debouncing and backend rate-limiting per client IP/session.

---

### Edge Case 5.4: Network Timeouts & Upstream API Latency Spikes
- **Scenario:** The external LLM API (OpenAI / Anthropic) experiences latency spikes or outages, hanging for $>15$ seconds.
- **Failure Mode:** The chat UI freezes indefinitely, leaving the user with a broken spinner and no feedback.
- **Detection:** Request elapsed time $> 10$ seconds.
- **Mitigation Strategy:**
  - Set a 10-second timeout on the FastAPI backend LLM invocation.
  - Return a graceful error message:
    > *"Our assistant is temporarily experiencing delays. Please try asking your question again in a moment."*
  - Add a visible "Retry" button on the UI.

---

### Edge Case 5.5: Mobile Viewport & Citation Overflow
- **Scenario:** On small screens (e.g., iPhone SE / 375px width), the long Groww URL (`https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth`) breaks layout horizontally, or the compliance disclaimer is pushed offscreen.
- **Failure Mode:** Horizontal scrollbars appear; UI elements overlap; compliance disclaimer becomes invisible without scrolling.
- **Detection:** Viewport width tests under 360px and 768px.
- **Mitigation Strategy:**
  - Apply CSS `overflow-wrap: break-word;` and `word-break: break-all;` to chat message bubbles and links.
  - Sticky header for the mandatory disclaimer banner:
    `"Facts-only. No investment advice."` remains anchored and visible at the top of the viewport at all times.

---

## 3. UI/API Security & Stability Checklist

| Safeguard | Implementation | Status |
| :--- | :--- | :--- |
| **Max Query Length** | Limit to 300 characters (Pydantic + HTML attribute) | Enforced |
| **Empty Input Check** | Reject empty strings and whitespace-only submissions | Enforced |
| **XSS Prevention** | `DOMPurify` / Text node rendering | Enforced |
| **Sticky Disclaimer** | High-contrast banner fixed at top of interface | Enforced |
| **Quick Action Pills** | Pre-populated, non-editable 1-click sample prompts | Enforced |
