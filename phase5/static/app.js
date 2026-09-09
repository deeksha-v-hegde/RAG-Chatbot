/**
 * Grow RAG Chatbot Client Script
 * Implements high-fidelity UI matching the approved mockup.
 */

document.addEventListener("DOMContentLoaded", () => {
  const chatForm = document.getElementById("chatForm");
  const queryInput = document.getElementById("queryInput");
  const sendBtn = document.getElementById("sendBtn");
  const emptyHero = document.getElementById("emptyHero");
  const messagesContainer = document.getElementById("messagesContainer");
  const messagesList = document.getElementById("messagesList");
  const chatViewport = document.getElementById("chatViewport");
  const clearChatBtn = document.getElementById("clearChatBtn");
  const exampleCards = document.querySelectorAll(".example-card");
  const lastUpdatedTimestamp = document.getElementById("lastUpdatedTimestamp");

  // Format current timestamp
  if (lastUpdatedTimestamp) {
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    lastUpdatedTimestamp.textContent = `LAST UPDATED: TODAY, ${timeStr}`;
  }

  // Clear Chat Button
  if (clearChatBtn) {
    clearChatBtn.addEventListener("click", () => {
      messagesList.innerHTML = "";
      messagesContainer.style.display = "none";
      if (emptyHero) {
        emptyHero.style.display = "flex";
      }
      queryInput.value = "";
      queryInput.focus();
    });
  }

  // Sidebar Navigation Items
  const navHome = document.getElementById("navHome");
  const navFaq = document.getElementById("navFaq");
  const navTrends = document.getElementById("navTrends");
  const navHistory = document.getElementById("navHistory");

  if (navHome) {
    navHome.addEventListener("click", () => {
      messagesList.innerHTML = "";
      messagesContainer.style.display = "none";
      if (emptyHero) emptyHero.style.display = "flex";
      queryInput.value = "";
    });
  }
  if (navFaq) {
    navFaq.addEventListener("click", () => {
      const q = "What is the expense ratio and exit load of designated HDFC schemes?";
      queryInput.value = q;
      submitQuery(q);
    });
  }
  if (navTrends) {
    navTrends.addEventListener("click", () => {
      const q = "What benchmarks do designated HDFC mutual fund schemes track?";
      queryInput.value = q;
      submitQuery(q);
    });
  }
  if (navHistory) {
    navHistory.addEventListener("click", () => {
      const q = "What is the history and launch date of HDFC Equity Fund?";
      queryInput.value = q;
      submitQuery(q);
    });
  }

  // Example Questions in Sidebar
  exampleCards.forEach((card) => {
    card.addEventListener("click", () => {
      const q = card.getAttribute("data-query");
      if (q) {
        queryInput.value = q;
        submitQuery(q);
      }
    });
  });

  // Form Submit
  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const q = queryInput.value.trim();
    if (q) {
      submitQuery(q);
    }
  });

  // Handle Enter Key
  queryInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      const q = queryInput.value.trim();
      if (q) {
        submitQuery(q);
      }
    }
  });

  async function submitQuery(text) {
    // Hide empty hero, show messages
    if (emptyHero) emptyHero.style.display = "none";
    if (messagesContainer) messagesContainer.style.display = "block";

    // 1. Add User Message
    appendUserBubble(text);
    queryInput.value = "";
    queryInput.disabled = true;
    sendBtn.disabled = true;

    // 2. Add Temporary Loading Assistant Card
    const loadingRow = appendLoadingCard();
    scrollToBottom();

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: text }),
      });

      if (!res.ok) {
        throw new Error(`Server returned HTTP ${res.status}`);
      }

      const data = await res.json();
      loadingRow.remove();
      appendAssistantCard(data);
    } catch (err) {
      console.error("Chat Error:", err);
      loadingRow.remove();
      appendAssistantCard({
        answer: "Unable to retrieve verified data at this moment. Please verify the backend service is running.",
        citation_url: "",
        citation_title: "",
        last_updated: "2026-09-09",
        is_refusal: true,
        is_unknown: true,
        url_count: 0
      });
    } finally {
      queryInput.disabled = false;
      sendBtn.disabled = false;
      queryInput.focus();
      scrollToBottom();
    }
  }

  function appendUserBubble(text) {
    const row = document.createElement("div");
    row.className = "user-msg-row";
    row.innerHTML = `<div class="user-bubble">${escapeHtml(text)}</div>`;
    messagesList.appendChild(row);
  }

  function appendLoadingCard() {
    const row = document.createElement("div");
    row.className = "assistant-msg-row";
    row.innerHTML = `
      <div class="assistant-avatar">🛡️</div>
      <div class="assistant-card" style="opacity: 0.8;">
        <div class="verified-badge">
          <span class="green-dot"></span>
          <span>Synthesizing verified response...</span>
        </div>
        <div class="answer-body" style="color: #94A3B8;">Querying verified disclosures and applying compliance guardrails...</div>
      </div>
    `;
    messagesList.appendChild(row);
    return row;
  }

  function appendAssistantCard(data) {
    const row = document.createElement("div");
    row.className = "assistant-msg-row";

    let sourcesHtml = "";
    if (data.citation_url && data.url_count > 0) {
      const domainDisplay = data.citation_url.replace("https://", "").replace("http://", "");
      sourcesHtml = `
        <div class="sources-box">
          <div class="sources-label">Sources</div>
          <a href="${escapeHtml(data.citation_url)}" target="_blank" rel="noopener noreferrer" class="source-link-btn">
            <span class="green-dot"></span>
            <span>${escapeHtml(domainDisplay)}</span>
            <span>↗</span>
          </a>
          <div class="source-meta-text">
            <span class="green-dot"></span>
            <span>Verified from 1 source · ${escapeHtml(data.last_updated || '2026-09-09')}</span>
          </div>
        </div>
      `;
    } else if (data.is_unknown || data.answer.toLowerCase().includes("personal information")) {
      sourcesHtml = `
        <div class="sources-box">
          <div class="zero-url-pill">
            <span>🛡️</span>
            <span>Zero-URL Defense Enforced · No external URLs attached</span>
          </div>
        </div>
      `;
    }

    // Format paragraphs and bullets
    const formattedAnswer = formatAnswer(data.answer);

    row.innerHTML = `
      <div class="assistant-avatar">🛡️</div>
      <div class="assistant-card">
        <div class="verified-badge">
          <span class="green-dot"></span>
          <span>Verified Answer</span>
        </div>
        <div class="answer-body">
          ${formattedAnswer}
        </div>
        ${sourcesHtml}
        <div class="card-actions">
          <span class="card-action-btn" title="Helpful">👍</span>
          <span class="card-action-btn" title="Not helpful">👎</span>
          <span class="card-action-btn copy-btn" title="Copy answer">📋</span>
        </div>
      </div>
    `;

    // Copy to clipboard
    const copyBtn = row.querySelector(".copy-btn");
    if (copyBtn) {
      copyBtn.addEventListener("click", () => {
        navigator.clipboard.writeText(data.markdown_output || data.answer).then(() => {
          copyBtn.textContent = "✓ Copied";
          setTimeout(() => {
            copyBtn.textContent = "📋";
          }, 2000);
        });
      });
    }

    messagesList.appendChild(row);
  }

  function formatAnswer(text) {
    if (!text) return "";
    let lines = text.split("\n").filter(l => l.trim().length > 0);
    let output = "";
    let inList = false;

    lines.forEach(line => {
      let trimmed = line.trim();
      if (trimmed.startsWith("•") || trimmed.startsWith("-") || trimmed.startsWith("*")) {
        if (!inList) {
          output += "<ul>";
          inList = true;
        }
        output += `<li>${escapeHtml(trimmed.replace(/^[-•*]\s*/, ""))}</li>`;
      } else {
        if (inList) {
          output += "</ul>";
          inList = false;
        }
        output += `<p style="margin-bottom: 8px;">${escapeHtml(trimmed)}</p>`;
      }
    });

    if (inList) {
      output += "</ul>";
    }
    return output;
  }

  function scrollToBottom() {
    chatViewport.scrollTop = chatViewport.scrollHeight;
  }

  function escapeHtml(str) {
    if (!str) return "";
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }
});
