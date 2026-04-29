import { useState, useEffect, useCallback } from "react";

// ─── Question Banks ────────────────────────────────────────────────────────────
// Each evening question has 7 weekly rotations + follow-up prompts per rotation

const EVENING_QUESTION_BANK = [
  {
    id: "mattered",
    icon: "✦",
    color: "#C8A96E",
    rotations: [
      { label: "What did I do today that I'm quietly proud of?", hint: "It doesn't need to be big. Showing up counts.", followUp: "What made that feel meaningful to you specifically?" },
      { label: "Where did I show up fully today?", hint: "A moment of presence, effort, or care.", followUp: "What would have been easier to avoid — but you didn't?" },
      { label: "What did I do today that mattered to someone else?", hint: "Even a small act of attention or kindness.", followUp: "How do you think it landed for them?" },
      { label: "What work or effort am I glad I put in today?", hint: "Something that required something from you.", followUp: "What does it feel like to have done it?" },
      { label: "What did I create, complete, or move forward today?", hint: "No matter how small the progress.", followUp: "What's one next step that feels natural from here?" },
      { label: "What decision today aligned with who I want to be?", hint: "A choice that felt right, even if hard.", followUp: "What made it the right call?" },
      { label: "What did I give today — time, attention, or energy?", hint: "Generosity takes many forms.", followUp: "Did giving that feel costly or natural?" },
    ],
  },
  {
    id: "given",
    icon: "◎",
    color: "#7EB8A4",
    rotations: [
      { label: "What was I given today that I didn't earn?", hint: "Good weather, a kind word, your health, a laugh.", followUp: "Did you notice it in the moment, or only now?" },
      { label: "What happened today that I didn't plan but benefited from?", hint: "A surprise, a stroke of luck, an unexpected kindness.", followUp: "What would the day have looked like without it?" },
      { label: "What beauty did I encounter today?", hint: "In nature, people, a moment, a sound.", followUp: "Did you pause for it, or catch it in passing?" },
      { label: "Who supported me today, even quietly?", hint: "A kind word, presence, patience, or just being there.", followUp: "Have you told them — or could you?" },
      { label: "What did my body do well for me today?", hint: "Movement, rest, healing, senses.", followUp: "What do you take for granted that deserves acknowledgment?" },
      { label: "What ordinary moment today was actually quite good?", hint: "Coffee, a quiet minute, a comfortable chair.", followUp: "What would have to be absent for you to truly miss it?" },
      { label: "What did I learn or understand better today?", hint: "An insight, a reframe, a new perspective.", followUp: "How might this change how you approach something?" },
    ],
  },
  {
    id: "release",
    icon: "◇",
    color: "#A89BC2",
    rotations: [
      { label: "What can I let go of from today?", hint: "Name it. You don't have to solve it — just set it down.", followUp: "What would it feel like to wake up tomorrow without carrying this?" },
      { label: "What worry followed me through today that I can put down now?", hint: "Naming it is enough. It doesn't need a solution tonight.", followUp: "Is this something you can act on, or only accept?" },
      { label: "What comparison or expectation weighed on me today?", hint: "An unfair standard you held yourself to.", followUp: "Where did that standard come from — and is it actually yours?" },
      { label: "What conversation or moment am I replaying unhelpfully?", hint: "The loop that isn't helping you improve, just ruminating.", followUp: "What's the one thing you'd do differently — then release the rest?" },
      { label: "What unfinished thing is okay to leave unfinished tonight?", hint: "Not everything needs to be resolved before sleep.", followUp: "What would 'good enough for today' look like here?" },
      { label: "What emotion from today deserves acknowledgment before I sleep?", hint: "Frustration, sadness, disappointment — they lighten when named.", followUp: "What did that emotion want you to notice?" },
      { label: "What did I hold too tightly today that I can loosen my grip on?", hint: "An outcome, an opinion, a need to be right.", followUp: "What becomes possible if you hold it more lightly?" },
    ],
  },
];

const MORNING_BANK = [
  { prompt: "What would make today feel complete?", followUp: "What's the single most important thing — not urgent, but meaningful?" },
  { prompt: "What is one thing I want to bring full attention to today?", followUp: "What usually pulls your attention away from this?" },
  { prompt: "What am I carrying into today that I could set down?", followUp: "If you set it down, what becomes lighter?" },
  { prompt: "What small act of care can I offer someone today?", followUp: "Who specifically comes to mind?" },
  { prompt: "What does 'enough' look like for me today?", followUp: "How will you know when you've reached it?" },
  { prompt: "What am I grateful for before the day begins?", followUp: "What would today look like if this were absent?" },
  { prompt: "What would I regret not doing today?", followUp: "What's stopping you — and is that obstacle real?" },
  { prompt: "Who do I want to show up as today?", followUp: "What's one concrete way that version of you would act?" },
  { prompt: "What am I resisting that might be worth leaning into today?", followUp: "What's the fear underneath the resistance?" },
  { prompt: "What is already good about today before it begins?", followUp: "How can you protect or build on that?" },
  { prompt: "What do I want less of today — and what would replace it?", followUp: "What's the smallest possible first step?" },
  { prompt: "What truth do I need to tell myself this morning?", followUp: "What's easier to ignore — and why does it matter?" },
  { prompt: "What would a content version of me do today?", followUp: "Pick one moment today where you'll practice that." },
  { prompt: "What am I looking forward to, even slightly?", followUp: "How can you make sure it actually happens?" },
];

const STORAGE_KEY = "still_entries_v3";
const REMINDERS_KEY = "still_reminders";

// ─── Helpers ──────────────────────────────────────────────────────────────────

const getTodayKey = () => new Date().toISOString().split("T")[0];

const formatDate = (dateStr) => {
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" });
};

const formatShortDate = (dateStr) => {
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
};

// Get question rotation index based on date (cycles every 7 days)
const getRotationIndex = (dateStr) => {
  const d = new Date(dateStr + "T00:00:00");
  const epoch = new Date("2024-01-01T00:00:00");
  const daysSinceEpoch = Math.floor((d - epoch) / 86400000);
  return daysSinceEpoch % 7;
};

const getDailyMorning = (dateStr) => {
  const idx = getRotationIndex(dateStr);
  return MORNING_BANK[idx % MORNING_BANK.length];
};

const getTodayQuestions = (dateStr) => {
  const idx = getRotationIndex(dateStr);
  return EVENING_QUESTION_BANK.map((bank) => ({
    id: bank.id,
    icon: bank.icon,
    color: bank.color,
    ...bank.rotations[idx],
  }));
};

const loadData = (key) => {
  try { return JSON.parse(localStorage.getItem(key) || "{}"); }
  catch { return {}; }
};
const saveData = (key, val) => localStorage.setItem(key, JSON.stringify(val));

// ─── Bottom Nav ───────────────────────────────────────────────────────────────

function BottomNav({ view, setView }) {
  const tabs = [
    { id: "home", label: "Today", icon: "◎" },
    { id: "morning", label: "Morning", icon: "○" },
    { id: "weekly", label: "Week", icon: "▦" },
    { id: "history", label: "History", icon: "≡" },
    { id: "reminders", label: "Reminders", icon: "◷" },
  ];
  return (
    <div style={S.nav}>
      {tabs.map((t) => (
        <button key={t.id} style={{ ...S.navBtn, color: view === t.id ? "#C8A96E" : "#3a3530" }} onClick={() => setView(t.id)}>
          <span style={S.navIcon}>{t.icon}</span>
          <span style={S.navLabel}>{t.label}</span>
        </button>
      ))}
    </div>
  );
}

// ─── Morning View ─────────────────────────────────────────────────────────────

function MorningView({ entries, setEntries, todayKey }) {
  const todayEntry = entries[todayKey] || {};
  const morning = getDailyMorning(todayKey);
  const [phase, setPhase] = useState(todayEntry.morning ? "done" : "prompt"); // prompt | followup | done
  const [answer1, setAnswer1] = useState(todayEntry.morning?.answer1 || "");
  const [answer2, setAnswer2] = useState(todayEntry.morning?.answer2 || "");
  const [animating, setAnimating] = useState(false);

  const goToFollowUp = () => {
    setAnimating(true);
    setTimeout(() => { setPhase("followup"); setAnimating(false); }, 280);
  };

  const handleSave = () => {
    const updated = {
      ...entries,
      [todayKey]: { ...(entries[todayKey] || {}), morning: { answer1, answer2, prompt: morning.prompt, followUp: morning.followUp }, date: todayKey },
    };
    saveData(STORAGE_KEY, updated);
    setEntries(updated);
    setPhase("done");
  };

  return (
    <div style={S.page}>
      <div style={S.sectionHeader}>
        <div style={{ ...S.sectionIcon, color: "#E8C17A" }}>○</div>
        <div>
          <h2 style={S.sectionTitle}>Morning Intention</h2>
          <p style={S.sectionSub}>{formatDate(todayKey)}</p>
        </div>
      </div>

      {phase === "done" ? (
        <div>
          <div style={S.doneBadge}>✦ Morning intention set</div>
          <div style={S.completeSummary}>
            <div style={S.summaryItem}>
              <div style={{ fontSize: 14, color: "#E8C17A", flexShrink: 0 }}>○</div>
              <div>
                <div style={S.summaryLabel}>{todayEntry.morning?.prompt || morning.prompt}</div>
                <div style={S.summaryAnswer}>{todayEntry.morning?.answer1 || answer1}</div>
              </div>
            </div>
            {(todayEntry.morning?.answer2 || answer2) && (
              <div style={S.summaryItem}>
                <div style={{ fontSize: 14, color: "#E8C17A", flexShrink: 0 }}>↳</div>
                <div>
                  <div style={S.summaryLabel}>{todayEntry.morning?.followUp || morning.followUp}</div>
                  <div style={S.summaryAnswer}>{todayEntry.morning?.answer2 || answer2}</div>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div style={{ opacity: animating ? 0 : 1, transition: "opacity 0.28s" }}>
          <div style={S.promptCard}>
            <div style={S.promptLabel}>{phase === "prompt" ? "Today's question" : "Follow-up"}</div>
            <div style={S.promptText}>{phase === "prompt" ? morning.prompt : morning.followUp}</div>
          </div>
          <textarea
            style={{ ...S.textarea, borderColor: (phase === "prompt" ? answer1 : answer2) ? "#E8C17A" : "#2a2a2a", minHeight: 130 }}
            placeholder="Write freely, no judgment..."
            value={phase === "prompt" ? answer1 : answer2}
            onChange={(e) => phase === "prompt" ? setAnswer1(e.target.value) : setAnswer2(e.target.value)}
            autoFocus
          />
          <div style={{ display: "flex", gap: 10, marginTop: 16 }}>
            {phase === "prompt" ? (
              <>
                <button
                  style={{ ...S.primaryBtn, background: "#E8C17A", flex: 2, opacity: answer1.trim() ? 1 : 0.4 }}
                  onClick={goToFollowUp} disabled={!answer1.trim()}
                >Follow-up →</button>
                <button style={{ ...S.ghostBtn, flex: 1 }} onClick={() => { if (answer1.trim()) handleSave(); }}>Skip & Save</button>
              </>
            ) : (
              <>
                <button style={{ ...S.ghostBtn, flex: 1 }} onClick={() => { setAnimating(true); setTimeout(() => { setPhase("prompt"); setAnimating(false); }, 280); }}>← Back</button>
                <button style={{ ...S.primaryBtn, background: "#E8C17A", flex: 2, opacity: answer2.trim() ? 1 : 0.4 }} onClick={handleSave} disabled={!answer2.trim()}>Set Intention ✦</button>
              </>
            )}
          </div>
        </div>
      )}
      <div style={S.morningTip}><span style={{ color: "#E8C17A" }}>◦</span> Write before checking your phone. The first 5 minutes shape the day's tone.</div>
    </div>
  );
}

// ─── Evening Flow ─────────────────────────────────────────────────────────────

function EveningFlow({ entries, setEntries, onComplete, onBack, todayKey }) {
  const todayEntry = entries[todayKey] || {};
  const alreadySaved = !!todayEntry.evening;
  const questions = getTodayQuestions(todayKey);

  const emptyAnswers = () => Object.fromEntries(questions.map((q) => [q.id, { main: "", followUp: "" }]));
  const [answers, setAnswers] = useState(todayEntry.evening?.answers || emptyAnswers());
  const [step, setStep] = useState(0);
  const [subStep, setSubStep] = useState("main"); // main | followup
  const [animating, setAnimating] = useState(false);

  const currentQ = questions[step];
  const totalSteps = questions.length;
  const progress = (step / totalSteps) * 100 + (subStep === "followup" ? (1 / totalSteps) * 50 : 0);

  const transition = (fn) => { setAnimating(true); setTimeout(() => { fn(); setAnimating(false); }, 280); };

  const handleMain = (val) => setAnswers((p) => ({ ...p, [currentQ.id]: { ...p[currentQ.id], main: val } }));
  const handleFollowUp = (val) => setAnswers((p) => ({ ...p, [currentQ.id]: { ...p[currentQ.id], followUp: val } }));

  const next = () => {
    if (subStep === "main") {
      transition(() => setSubStep("followup"));
    } else if (step < totalSteps - 1) {
      transition(() => { setStep((s) => s + 1); setSubStep("main"); });
    } else {
      const updated = { ...entries, [todayKey]: { ...(entries[todayKey] || {}), evening: { answers, questions: questions.map((q) => ({ id: q.id, label: q.label, followUp: q.followUp })) }, date: todayKey } };
      saveData(STORAGE_KEY, updated);
      setEntries(updated);
      onComplete(answers, questions);
    }
  };

  const back = () => {
    if (subStep === "followup") transition(() => setSubStep("main"));
    else if (step > 0) transition(() => { setStep((s) => s - 1); setSubStep("followup"); });
    else onBack();
  };

  const skipFollowUp = () => {
    if (step < totalSteps - 1) transition(() => { setStep((s) => s + 1); setSubStep("main"); });
    else {
      const updated = { ...entries, [todayKey]: { ...(entries[todayKey] || {}), evening: { answers, questions: questions.map((q) => ({ id: q.id, label: q.label, followUp: q.followUp })) }, date: todayKey } };
      saveData(STORAGE_KEY, updated);
      setEntries(updated);
      onComplete(answers, questions);
    }
  };

  if (alreadySaved) {
    const savedQs = todayEntry.evening?.questions || questions;
    const savedAs = todayEntry.evening?.answers || answers;
    return (
      <div style={S.page}>
        <button style={S.backBtn} onClick={onBack}>← Back</button>
        <div style={{ textAlign: "center", paddingTop: 16, marginBottom: 20 }}>
          <div style={{ fontSize: 34, color: "#7EB8A4", marginBottom: 8 }}>◎</div>
          <h2 style={{ ...S.sectionTitle, textAlign: "center" }}>Today's reflection is complete.</h2>
        </div>
        <div style={S.completeSummary}>
          {savedQs.map((q) => (
            <div key={q.id} style={{ marginBottom: 16 }}>
              <div style={S.summaryItem}>
                <div style={{ fontSize: 14, color: questions.find((x) => x.id === q.id)?.color || "#C8A96E", flexShrink: 0 }}>
                  {questions.find((x) => x.id === q.id)?.icon || "◎"}
                </div>
                <div>
                  <div style={S.summaryLabel}>{q.label}</div>
                  <div style={S.summaryAnswer}>{savedAs[q.id]?.main}</div>
                </div>
              </div>
              {savedAs[q.id]?.followUp && (
                <div style={{ ...S.summaryItem, marginTop: 8, paddingLeft: 22 }}>
                  <div style={{ fontSize: 12, color: "#4a4540", flexShrink: 0 }}>↳</div>
                  <div>
                    <div style={S.summaryLabel}>{q.followUp}</div>
                    <div style={S.summaryAnswer}>{savedAs[q.id]?.followUp}</div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  }

  const isFollowUp = subStep === "followup";
  const currentAnswer = isFollowUp ? answers[currentQ.id]?.followUp : answers[currentQ.id]?.main;

  return (
    <div style={S.page}>
      <div style={S.reflectHeader}>
        <button style={{ ...S.backBtn, padding: 0 }} onClick={back}>←</button>
        <div style={S.progressBar}><div style={{ ...S.progressFill, width: `${progress}%`, background: currentQ.color }} /></div>
        <span style={S.stepCount}>{step + 1}/{totalSteps} {isFollowUp ? "↳" : ""}</span>
      </div>

      <div style={{ ...S.questionCard, opacity: animating ? 0 : 1, transition: "opacity 0.28s" }}>
        {isFollowUp ? (
          <>
            <div style={{ fontSize: 13, color: "#4a4540", letterSpacing: "0.08em", marginBottom: 4 }}>Follow-up</div>
            <div style={{ fontSize: 14, color: currentQ.color, fontStyle: "italic", marginBottom: 16, lineHeight: 1.5 }}>↳ {currentQ.followUp}</div>
          </>
        ) : (
          <>
            <div style={{ fontSize: 26, color: currentQ.color, marginBottom: 6 }}>{currentQ.icon}</div>
            <h2 style={S.qLabel}>{currentQ.label}</h2>
            <p style={S.qHint}>{currentQ.hint}</p>
          </>
        )}
        <textarea
          style={{ ...S.textarea, borderColor: currentAnswer ? currentQ.color : "#2a2a2a" }}
          placeholder={isFollowUp ? "Go a little deeper..." : "Write freely, no judgment..."}
          value={currentAnswer || ""}
          onChange={(e) => isFollowUp ? handleFollowUp(e.target.value) : handleMain(e.target.value)}
          rows={isFollowUp ? 4 : 5}
          autoFocus
        />
      </div>

      <div style={S.navRow}>
        {isFollowUp && (
          <button style={S.ghostBtn} onClick={skipFollowUp}>Skip</button>
        )}
        <button
          style={{ ...S.primaryBtn, background: currentQ.color, marginLeft: isFollowUp ? 0 : "auto", width: "auto", opacity: currentAnswer?.trim() ? 1 : isFollowUp ? 0.5 : 0.4 }}
          onClick={next}
          disabled={!isFollowUp && !currentAnswer?.trim()}
        >
          {!isFollowUp ? "Follow-up →" : step < totalSteps - 1 ? "Next ✦" : "Complete Day ✦"}
        </button>
      </div>
    </div>
  );
}

// ─── Home View ────────────────────────────────────────────────────────────────

function HomeView({ entries, setEntries, todayKey }) {
  const [subview, setSubview] = useState("home");
  const [completedData, setCompletedData] = useState(null);
  const todayEntry = entries[todayKey] || {};
  const morningDone = !!todayEntry.morning;
  const eveningDone = !!todayEntry.evening;
  const questions = getTodayQuestions(todayKey);

  // Reset subview when date changes
  useEffect(() => { setSubview("home"); }, [todayKey]);

  if (subview === "evening") {
    return <EveningFlow entries={entries} setEntries={setEntries} todayKey={todayKey}
      onComplete={(ans, qs) => { setCompletedData({ ans, qs }); setSubview("complete"); }} onBack={() => setSubview("home")} />;
  }

  if (subview === "complete" && completedData) {
    const { ans, qs } = completedData;
    return (
      <div style={S.page}>
        <div style={S.completeCenter}>
          <div style={{ fontSize: 44, color: "#7EB8A4", marginBottom: 8 }}>◎</div>
          <h2 style={{ fontSize: 28, fontWeight: 400, margin: 0, color: "#f0ead8", letterSpacing: "0.04em" }}>Day complete.</h2>
          <p style={{ fontSize: 13, color: "#5a5550", textAlign: "center", fontStyle: "italic", lineHeight: 1.6, maxWidth: 280, margin: "4px 0 14px" }}>You've done the work of noticing. That's enough.</p>
          <div style={{ ...S.completeSummary, width: "100%" }}>
            {qs.map((q) => (
              <div key={q.id} style={{ marginBottom: ans[q.id]?.followUp ? 12 : 0 }}>
                <div style={S.summaryItem}>
                  <div style={{ fontSize: 14, color: questions.find((x) => x.id === q.id)?.color || "#C8A96E", flexShrink: 0 }}>
                    {questions.find((x) => x.id === q.id)?.icon}
                  </div>
                  <div>
                    <div style={S.summaryLabel}>{q.label}</div>
                    <div style={S.summaryAnswer}>{ans[q.id]?.main}</div>
                  </div>
                </div>
                {ans[q.id]?.followUp && (
                  <div style={{ ...S.summaryItem, marginTop: 7, paddingLeft: 20 }}>
                    <div style={{ fontSize: 11, color: "#3a3530", flexShrink: 0 }}>↳</div>
                    <div style={S.summaryAnswer}>{ans[q.id]?.followUp}</div>
                  </div>
                )}
              </div>
            ))}
          </div>
          <button style={S.primaryBtn} onClick={() => setSubview("home")}>Return Home</button>
        </div>
      </div>
    );
  }

  return (
    <div style={S.page}>
      <div style={S.homeHeader}>
        <div style={{ fontSize: 24, color: "#C8A96E" }}>◎</div>
        <h1 style={S.title}>Still</h1>
        <p style={S.subtitle}>A daily practice of contentment</p>
      </div>

      <div style={S.todayCard}>
        <div style={S.todayDate}>{formatDate(todayKey)}</div>
        <div style={S.streakRow}>
          <div style={{ ...S.pillBadge, background: morningDone ? "rgba(232,193,122,0.12)" : "transparent", color: morningDone ? "#E8C17A" : "#3a3530", borderColor: morningDone ? "#E8C17A" : "#2a2520" }}>
            {morningDone ? "✦" : "○"} Morning
          </div>
          <div style={{ ...S.pillBadge, background: eveningDone ? "rgba(126,184,164,0.12)" : "transparent", color: eveningDone ? "#7EB8A4" : "#3a3530", borderColor: eveningDone ? "#7EB8A4" : "#2a2520" }}>
            {eveningDone ? "✦" : "○"} Evening
          </div>
        </div>
      </div>

      {/* Preview today's questions */}
      <div style={S.questionPreviewCard}>
        <div style={S.questionPreviewLabel}>Tonight's questions</div>
        {questions.map((q) => (
          <div key={q.id} style={S.qPreviewRow}>
            <span style={{ color: q.color, fontSize: 13, flexShrink: 0 }}>{q.icon}</span>
            <span style={S.qPreviewText}>{q.label}</span>
          </div>
        ))}
      </div>

      <div style={S.actionCards}>
        <div style={S.actionCard}>
          <div style={{ fontSize: 17, color: "#E8C17A", marginBottom: 5 }}>○</div>
          <div style={S.actionCardTitle}>Morning Intention</div>
          <div style={S.actionCardSub}>{morningDone ? (todayEntry.morning?.answer1?.slice(0, 45) + (todayEntry.morning?.answer1?.length > 45 ? "..." : "")) : getDailyMorning(todayKey).prompt.slice(0, 45) + "..."}</div>
          {morningDone && <div style={{ fontSize: 9, color: "#E8C17A", marginTop: 7, letterSpacing: "0.1em" }}>SET ✦</div>}
        </div>
        <div style={{ ...S.actionCard, cursor: "pointer" }} onClick={() => setSubview("evening")}>
          <div style={{ fontSize: 17, color: "#7EB8A4", marginBottom: 5 }}>◎</div>
          <div style={S.actionCardTitle}>Evening Reflection</div>
          <div style={S.actionCardSub}>{eveningDone ? "Reflection complete" : "3 questions + follow-ups"}</div>
          <div style={{ fontSize: 9, color: "#7EB8A4", marginTop: 7, letterSpacing: "0.1em" }}>{eveningDone ? "REVIEW →" : "BEGIN →"}</div>
        </div>
      </div>

      <div style={S.quoteBlock}>
        <div style={S.quoteText}>"I have learned, in whatever state I am, to be content."</div>
        <div style={S.quoteAuthor}>— Philippians 4:11</div>
      </div>
    </div>
  );
}

// ─── Weekly View ──────────────────────────────────────────────────────────────

function WeeklyView({ entries, todayKey }) {
  const days = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(todayKey + "T00:00:00");
    d.setDate(d.getDate() - (6 - i));
    return d.toISOString().split("T")[0];
  });
  const weekEntries = days.map((d) => ({ date: d, entry: entries[d] || null }));
  const completedDays = weekEntries.filter((e) => e.entry?.evening).length;
  const morningDays = weekEntries.filter((e) => e.entry?.morning).length;

  const givenList = weekEntries.filter((e) => e.entry?.evening?.answers?.given?.main)
    .map((e) => ({ date: e.date, main: e.entry.evening.answers.given.main, followUp: e.entry.evening.answers.given.followUp }));

  const releaseList = weekEntries.filter((e) => e.entry?.evening?.answers?.release?.main)
    .map((e) => ({ date: e.date, main: e.entry.evening.answers.release.main, followUp: e.entry.evening.answers.release.followUp }));

  return (
    <div style={S.page}>
      <div style={S.sectionHeader}>
        <div style={{ ...S.sectionIcon, color: "#A89BC2" }}>▦</div>
        <div>
          <h2 style={S.sectionTitle}>Weekly Summary</h2>
          <p style={S.sectionSub}>Last 7 days</p>
        </div>
      </div>

      <div style={S.weekGrid}>
        {weekEntries.map(({ date, entry }) => (
          <div key={date} style={{ ...S.dayCell, borderColor: date === todayKey ? "#C8A96E" : "#1a1a1a" }}>
            <div style={S.dayCellLabel}>{new Date(date + "T00:00:00").toLocaleDateString("en-US", { weekday: "short" })}</div>
            <div style={S.dayCellDate}>{new Date(date + "T00:00:00").getDate()}</div>
            <div style={S.dayCellDots}>
              <span style={{ ...S.dot, background: entry?.morning ? "#E8C17A" : "#1a1a1a" }} />
              <span style={{ ...S.dot, background: entry?.evening ? "#7EB8A4" : "#1a1a1a" }} />
            </div>
          </div>
        ))}
      </div>

      <div style={S.statsRow}>
        <div style={S.statBox}><div style={{ ...S.statNum, color: "#7EB8A4" }}>{completedDays}/7</div><div style={S.statLabel}>Evening reflections</div></div>
        <div style={S.statBox}><div style={{ ...S.statNum, color: "#E8C17A" }}>{morningDays}/7</div><div style={S.statLabel}>Morning intentions</div></div>
        <div style={S.statBox}><div style={{ ...S.statNum, color: "#A89BC2" }}>{givenList.length}</div><div style={S.statLabel}>Gifts noticed</div></div>
      </div>

      {givenList.length > 0 && (
        <div style={S.threadSection}>
          <div style={S.threadTitle}><span style={{ color: "#7EB8A4" }}>◎</span> What you received this week</div>
          {givenList.map(({ date, main, followUp }) => (
            <div key={date} style={S.threadItem}>
              <div style={S.threadDate}>{formatShortDate(date)}</div>
              <div>
                <div style={S.threadText}>{main}</div>
                {followUp && <div style={{ ...S.threadText, color: "#3a3530", marginTop: 3, fontSize: 11 }}>↳ {followUp}</div>}
              </div>
            </div>
          ))}
        </div>
      )}

      {releaseList.length > 0 && (
        <div style={S.threadSection}>
          <div style={S.threadTitle}><span style={{ color: "#A89BC2" }}>◇</span> What you released this week</div>
          {releaseList.map(({ date, main, followUp }) => (
            <div key={date} style={S.threadItem}>
              <div style={S.threadDate}>{formatShortDate(date)}</div>
              <div>
                <div style={S.threadText}>{main}</div>
                {followUp && <div style={{ ...S.threadText, color: "#3a3530", marginTop: 3, fontSize: 11 }}>↳ {followUp}</div>}
              </div>
            </div>
          ))}
        </div>
      )}

      {completedDays === 0 && <div style={S.emptyState}>Complete your first evening reflection to see your weekly summary here.</div>}
    </div>
  );
}

// ─── History View ─────────────────────────────────────────────────────────────

function HistoryView({ entries }) {
  const [selected, setSelected] = useState(null);
  const sorted = Object.values(entries).filter((e) => e.evening || e.morning).sort((a, b) => b.date.localeCompare(a.date));

  if (selected) {
    const entry = entries[selected];
    const qs = entry.evening?.questions || getTodayQuestions(selected);
    const as = entry.evening?.answers || {};
    return (
      <div style={S.page}>
        <button style={S.backBtn} onClick={() => setSelected(null)}>← Back</button>
        <div style={{ ...S.todayDate, marginBottom: 22 }}>{formatDate(selected)}</div>

        {entry.morning && (
          <div style={{ marginBottom: 26 }}>
            <div style={{ ...S.threadTitle, marginBottom: 10 }}><span style={{ color: "#E8C17A" }}>○</span> Morning Intention</div>
            <div style={S.entrySectionAnswer}>{entry.morning.answer1}</div>
            {entry.morning.answer2 && (
              <div style={{ marginTop: 10, paddingLeft: 14, borderLeft: "1px solid #1a1a1a" }}>
                <div style={S.summaryLabel}>{entry.morning.followUp}</div>
                <div style={S.entrySectionAnswer}>{entry.morning.answer2}</div>
              </div>
            )}
          </div>
        )}

        {entry.evening && (
          <div style={S.entryFull}>
            {qs.map((q) => {
              const qDef = EVENING_QUESTION_BANK.find((b) => b.id === q.id);
              return (
                <div key={q.id} style={{ marginBottom: 8 }}>
                  <div style={S.entrySection}>
                    <div style={{ fontSize: 17, color: qDef?.color || "#C8A96E", flexShrink: 0, marginTop: 2 }}>{qDef?.icon || "◎"}</div>
                    <div>
                      <div style={S.entrySectionLabel}>{q.label}</div>
                      <div style={S.entrySectionAnswer}>{as[q.id]?.main}</div>
                    </div>
                  </div>
                  {as[q.id]?.followUp && (
                    <div style={{ paddingLeft: 30, marginTop: 8 }}>
                      <div style={S.summaryLabel}>{q.followUp}</div>
                      <div style={{ ...S.entrySectionAnswer, fontSize: 13, color: "#6a6258" }}>{as[q.id]?.followUp}</div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    );
  }

  return (
    <div style={S.page}>
      <div style={S.sectionHeader}>
        <div style={{ ...S.sectionIcon, color: "#9a9188" }}>≡</div>
        <div>
          <h2 style={S.sectionTitle}>Past Reflections</h2>
          <p style={S.sectionSub}>{sorted.length} entries</p>
        </div>
      </div>
      {sorted.length === 0 && <div style={S.emptyState}>No entries yet. Begin your first reflection from the Today tab.</div>}
      <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
        {sorted.map((entry) => {
          const preview = entry.evening?.answers?.mattered?.main || entry.morning?.answer1 || "";
          return (
            <div key={entry.date} style={S.entryCard} onClick={() => setSelected(entry.date)}>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={S.entryDate}>{formatDate(entry.date)}</div>
                <div style={S.entryPreview}>{preview.slice(0, 65)}{preview.length > 65 ? "..." : ""}</div>
              </div>
              <div style={{ display: "flex", gap: 4, alignItems: "center", flexShrink: 0 }}>
                {entry.morning && <span style={{ fontSize: 9, color: "#E8C17A" }}>○</span>}
                {entry.evening && <span style={{ fontSize: 9, color: "#7EB8A4" }}>◎</span>}
                <span style={{ color: "#2a2520", fontSize: 13, marginLeft: 3 }}>→</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─── Reminders View ───────────────────────────────────────────────────────────

function RemindersView() {
  const [reminders, setReminders] = useState(() => loadData(REMINDERS_KEY));
  const [notifStatus, setNotifStatus] = useState("default");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (!("Notification" in window)) setNotifStatus("unsupported");
    else setNotifStatus(Notification.permission);
  }, []);

  const update = (key, val) => {
    const updated = { ...reminders, [key]: val };
    setReminders(updated);
    saveData(REMINDERS_KEY, updated);
    setSaved(true);
    setTimeout(() => setSaved(false), 1800);
  };

  const sendTest = (label) => {
    if (notifStatus === "granted") new Notification(`Still — ${label}`, { body: label === "Morning" ? "Set your intention for the day." : "Take 10 minutes to close the day." });
  };

  return (
    <div style={S.page}>
      <div style={S.sectionHeader}>
        <div style={{ ...S.sectionIcon, color: "#C8A96E" }}>◷</div>
        <div>
          <h2 style={S.sectionTitle}>Reminders</h2>
          <p style={S.sectionSub}>Build the daily habit</p>
        </div>
      </div>

      <div style={S.reminderCard}>
        <div style={S.reminderCardTitle}>Browser Notifications</div>
        {notifStatus === "unsupported" && <p style={S.reminderCardSub}>Your browser doesn't support notifications. Use your phone's clock app instead.</p>}
        {notifStatus === "default" && (<><p style={S.reminderCardSub}>Enable notifications so Still can nudge you at the right time.</p><button style={{ ...S.primaryBtn, marginTop: 10 }} onClick={async () => { const r = await Notification.requestPermission(); setNotifStatus(r); }}>Enable Notifications</button></>)}
        {notifStatus === "granted" && <div style={{ color: "#7EB8A4", fontSize: 13, marginTop: 4 }}>✦ Notifications enabled</div>}
        {notifStatus === "denied" && <p style={S.reminderCardSub}>Notifications are blocked. Update your browser settings to allow them from this page.</p>}
      </div>

      {[
        { key: "morning", label: "○ Morning Intention", sub: "Best before checking your phone", color: "#E8C17A", default: "07:00", testLabel: "Morning" },
        { key: "evening", label: "◎ Evening Reflection", sub: "Best 30–60 min before bed", color: "#7EB8A4", default: "21:00", testLabel: "Evening" },
        { key: "weekly", label: "▦ Weekly Review", sub: "Sunday evening reflection", color: "#A89BC2", default: "19:00", testLabel: null },
      ].map(({ key, label, sub, color, default: def, testLabel }) => (
        <div key={key} style={S.reminderCard}>
          <div style={S.reminderRow}>
            <div><div style={S.reminderCardTitle}>{label}</div><div style={S.reminderCardSub}>{sub}</div></div>
            <div style={{ ...S.toggleTrack, background: reminders[key + "On"] ? color : "#2a2520", cursor: "pointer" }} onClick={() => update(key + "On", !reminders[key + "On"])}>
              <div style={{ ...S.toggleThumb, transform: reminders[key + "On"] ? "translateX(20px)" : "translateX(2px)" }} />
            </div>
          </div>
          {reminders[key + "On"] && (
            <div style={{ marginTop: 14 }}>
              <label style={S.timeLabel}>{key === "weekly" ? "Sunday reminder time" : "Reminder time"}</label>
              <input type="time" style={S.timeInput} value={reminders[key + "Time"] || def} onChange={(e) => update(key + "Time", e.target.value)} />
              {testLabel && <button style={S.testBtn} onClick={() => sendTest(testLabel)}>Send test notification</button>}
            </div>
          )}
        </div>
      ))}

      {saved && <div style={S.savedBadge}>✦ Preferences saved</div>}
      <div style={S.reminderNote}>Note: Browser notifications only work while this page is open. For persistent daily reminders, add this page to your home screen and set phone alarms at these times.</div>
    </div>
  );
}

// ─── Root App ─────────────────────────────────────────────────────────────────

export default function App() {
  const [view, setView] = useState("home");
  const [entries, setEntries] = useState({});
  const [todayKey, setTodayKey] = useState(getTodayKey());

  useEffect(() => {
    setEntries(loadData(STORAGE_KEY));
  }, []);

  // ── Midnight auto-update detector ──
  useEffect(() => {
    const checkDate = () => {
      const current = getTodayKey();
      if (current !== todayKey) {
        setTodayKey(current);
        setEntries(loadData(STORAGE_KEY)); // reload entries so new day starts fresh
      }
    };
    const interval = setInterval(checkDate, 60000); // check every minute
    return () => clearInterval(interval);
  }, [todayKey]);

  return (
    <div style={S.root}>
      <div style={S.bg} />
      <div style={S.scrollArea}>
        {view === "home" && <HomeView entries={entries} setEntries={setEntries} todayKey={todayKey} />}
        {view === "morning" && <MorningView entries={entries} setEntries={setEntries} todayKey={todayKey} />}
        {view === "weekly" && <WeeklyView entries={entries} todayKey={todayKey} />}
        {view === "history" && <HistoryView entries={entries} />}
        {view === "reminders" && <RemindersView />}
      </div>
      <BottomNav view={view} setView={setView} />
    </div>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const S = {
  root: { minHeight: "100vh", background: "#0c0c0c", color: "#e8e2d9", fontFamily: "'Georgia','Times New Roman',serif", position: "relative", display: "flex", flexDirection: "column" },
  bg: { position: "fixed", inset: 0, background: "radial-gradient(ellipse at 15% 40%, rgba(200,169,110,0.05) 0%, transparent 55%), radial-gradient(ellipse at 85% 15%, rgba(126,184,164,0.04) 0%, transparent 50%)", pointerEvents: "none", zIndex: 0 },
  scrollArea: { flex: 1, overflowY: "auto", paddingBottom: 72, position: "relative", zIndex: 1 },
  page: { maxWidth: 520, margin: "0 auto", padding: "34px 20px 28px", display: "flex", flexDirection: "column" },
  nav: { position: "fixed", bottom: 0, left: 0, right: 0, background: "#0c0c0c", borderTop: "1px solid #1a1a1a", display: "flex", zIndex: 10 },
  navBtn: { flex: 1, background: "none", border: "none", cursor: "pointer", display: "flex", flexDirection: "column", alignItems: "center", padding: "10px 4px 14px", gap: 3, transition: "color 0.2s", fontFamily: "inherit" },
  navIcon: { fontSize: 16 },
  navLabel: { fontSize: 9, letterSpacing: "0.08em", textTransform: "uppercase" },
  homeHeader: { textAlign: "center", marginBottom: 28, paddingTop: 10 },
  title: { fontSize: 44, fontWeight: 400, margin: "6px 0 4px", letterSpacing: "0.08em", color: "#f0ead8" },
  subtitle: { fontSize: 10, color: "#3a3530", letterSpacing: "0.18em", textTransform: "uppercase", margin: 0 },
  todayCard: { border: "1px solid #1a1a1a", borderRadius: 2, padding: "14px 16px", marginBottom: 14, background: "rgba(255,255,255,0.015)" },
  todayDate: { fontSize: 10, color: "#3a3530", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 9 },
  streakRow: { display: "flex", gap: 7 },
  pillBadge: { fontSize: 10, border: "1px solid", borderRadius: 20, padding: "3px 11px", letterSpacing: "0.06em" },
  questionPreviewCard: { border: "1px solid #1a1a1a", borderRadius: 2, padding: "12px 16px", marginBottom: 14, background: "rgba(255,255,255,0.01)" },
  questionPreviewLabel: { fontSize: 9, color: "#3a3530", letterSpacing: "0.15em", textTransform: "uppercase", marginBottom: 10 },
  qPreviewRow: { display: "flex", gap: 10, alignItems: "flex-start", marginBottom: 7 },
  qPreviewText: { fontSize: 12, color: "#4a4540", lineHeight: 1.4, fontStyle: "italic" },
  actionCards: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 7, marginBottom: 20 },
  actionCard: { border: "1px solid #1a1a1a", borderRadius: 2, padding: "14px 13px", background: "rgba(255,255,255,0.012)", cursor: "default" },
  actionCardTitle: { fontSize: 11, color: "#a8a098", letterSpacing: "0.04em", marginBottom: 5 },
  actionCardSub: { fontSize: 10, color: "#2a2520", lineHeight: 1.5, fontStyle: "italic" },
  quoteBlock: { borderLeft: "1px solid #1a1a1a", paddingLeft: 13, marginTop: 4 },
  quoteText: { fontSize: 12, color: "#3a3530", fontStyle: "italic", lineHeight: 1.6, marginBottom: 3 },
  quoteAuthor: { fontSize: 9, color: "#2a2520", letterSpacing: "0.1em" },
  sectionHeader: { display: "flex", alignItems: "center", gap: 13, marginBottom: 22 },
  sectionIcon: { fontSize: 24, flexShrink: 0 },
  sectionTitle: { fontSize: 20, fontWeight: 400, margin: 0, color: "#f0ead8", letterSpacing: "0.03em" },
  sectionSub: { fontSize: 10, color: "#3a3530", margin: "3px 0 0", letterSpacing: "0.08em" },
  promptCard: { border: "1px solid #1a1a1a", borderRadius: 2, padding: "13px 15px", marginBottom: 16, background: "rgba(232,193,122,0.04)" },
  promptLabel: { fontSize: 9, color: "#3a3530", letterSpacing: "0.15em", textTransform: "uppercase", marginBottom: 6 },
  promptText: { fontSize: 15, color: "#d4c8a8", lineHeight: 1.5, fontStyle: "italic" },
  morningTip: { fontSize: 10, color: "#2a2520", lineHeight: 1.6, marginTop: 16, display: "flex", gap: 7 },
  reflectHeader: { display: "flex", alignItems: "center", gap: 13, marginBottom: 32 },
  progressBar: { flex: 1, height: 1, background: "#1a1a1a", borderRadius: 1, overflow: "hidden" },
  progressFill: { height: "100%", borderRadius: 1, transition: "width 0.4s ease, background 0.3s" },
  stepCount: { fontSize: 10, color: "#2a2520", letterSpacing: "0.1em", flexShrink: 0 },
  questionCard: { flex: 1, display: "flex", flexDirection: "column", gap: 12 },
  qLabel: { fontSize: 19, fontWeight: 400, lineHeight: 1.4, color: "#f0ead8", margin: 0 },
  qHint: { fontSize: 11, color: "#3a3530", lineHeight: 1.6, fontStyle: "italic", margin: 0 },
  textarea: { background: "rgba(255,255,255,0.025)", border: "1px solid #2a2a2a", borderRadius: 2, color: "#e8e2d9", fontFamily: "Georgia,serif", fontSize: 15, lineHeight: 1.7, padding: "12px", resize: "vertical", outline: "none", transition: "border-color 0.3s", marginTop: 5, width: "100%", boxSizing: "border-box" },
  navRow: { display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 22, gap: 10 },
  completeCenter: { display: "flex", flexDirection: "column", alignItems: "center", paddingTop: 28, gap: 10 },
  completeSummary: { display: "flex", flexDirection: "column", gap: 14, margin: "10px 0 18px", padding: "16px", border: "1px solid #1a1a1a", borderRadius: 2, background: "rgba(255,255,255,0.012)" },
  summaryItem: { display: "flex", gap: 10, alignItems: "flex-start" },
  summaryLabel: { fontSize: 9, color: "#2a2520", letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 3 },
  summaryAnswer: { fontSize: 13, color: "#a8a098", lineHeight: 1.6 },
  doneBadge: { fontSize: 12, color: "#7EB8A4", letterSpacing: "0.08em", padding: "10px 0 14px", textAlign: "center" },
  weekGrid: { display: "grid", gridTemplateColumns: "repeat(7,1fr)", gap: 3, marginBottom: 18 },
  dayCell: { border: "1px solid", borderRadius: 2, padding: "6px 2px", display: "flex", flexDirection: "column", alignItems: "center", gap: 3 },
  dayCellLabel: { fontSize: 7, color: "#2a2520", letterSpacing: "0.05em", textTransform: "uppercase" },
  dayCellDate: { fontSize: 12, color: "#a8a098" },
  dayCellDots: { display: "flex", gap: 2 },
  dot: { width: 4, height: 4, borderRadius: "50%", display: "inline-block" },
  statsRow: { display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 6, marginBottom: 22 },
  statBox: { border: "1px solid #1a1a1a", borderRadius: 2, padding: "11px 7px", textAlign: "center", background: "rgba(255,255,255,0.01)" },
  statNum: { fontSize: 19, fontWeight: 400, marginBottom: 3 },
  statLabel: { fontSize: 8, color: "#2a2520", letterSpacing: "0.06em", lineHeight: 1.4 },
  threadSection: { marginBottom: 20 },
  threadTitle: { fontSize: 11, color: "#4a4540", letterSpacing: "0.07em", marginBottom: 11, display: "flex", gap: 7, alignItems: "center" },
  threadItem: { display: "flex", gap: 10, marginBottom: 9, paddingBottom: 9, borderBottom: "1px solid #0f0f0f" },
  threadDate: { fontSize: 9, color: "#2a2520", minWidth: 36, paddingTop: 2, letterSpacing: "0.04em" },
  threadText: { fontSize: 12, color: "#5a5248", lineHeight: 1.5, fontStyle: "italic" },
  entryCard: { display: "flex", justifyContent: "space-between", alignItems: "center", gap: 9, padding: "13px 15px", border: "1px solid #111", borderRadius: 2, cursor: "pointer", background: "rgba(255,255,255,0.01)", marginBottom: 2 },
  entryDate: { fontSize: 11, color: "#C8A96E", marginBottom: 3, letterSpacing: "0.03em" },
  entryPreview: { fontSize: 10, color: "#2a2520", fontStyle: "italic", lineHeight: 1.4 },
  entryFull: { display: "flex", flexDirection: "column", gap: 20 },
  entrySection: { display: "flex", gap: 12, alignItems: "flex-start" },
  entrySectionLabel: { fontSize: 9, color: "#2a2520", letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 4 },
  entrySectionAnswer: { fontSize: 14, color: "#a8a098", lineHeight: 1.7 },
  reminderCard: { border: "1px solid #1a1a1a", borderRadius: 2, padding: "14px 15px", marginBottom: 7, background: "rgba(255,255,255,0.01)" },
  reminderRow: { display: "flex", justifyContent: "space-between", alignItems: "center" },
  reminderCardTitle: { fontSize: 12, color: "#a8a098", marginBottom: 2, letterSpacing: "0.03em" },
  reminderCardSub: { fontSize: 10, color: "#2a2520", lineHeight: 1.5, fontStyle: "italic", margin: "2px 0 0" },
  toggleTrack: { width: 42, height: 22, borderRadius: 11, position: "relative", transition: "background 0.25s", display: "block", flexShrink: 0 },
  toggleThumb: { position: "absolute", top: 2, width: 18, height: 18, borderRadius: "50%", background: "#0c0c0c", transition: "transform 0.25s" },
  timeLabel: { fontSize: 9, color: "#2a2520", letterSpacing: "0.1em", textTransform: "uppercase", display: "block", marginBottom: 6 },
  timeInput: { background: "rgba(255,255,255,0.04)", border: "1px solid #2a2a2a", borderRadius: 2, color: "#e8e2d9", fontFamily: "Georgia,serif", fontSize: 14, padding: "7px 10px", outline: "none", display: "block", marginBottom: 9 },
  testBtn: { background: "none", border: "1px solid #1a1a1a", borderRadius: 2, color: "#3a3530", fontSize: 9, letterSpacing: "0.08em", padding: "5px 10px", cursor: "pointer", fontFamily: "inherit" },
  reminderNote: { fontSize: 9, color: "#1a1a1a", lineHeight: 1.6, marginTop: 12, fontStyle: "italic" },
  primaryBtn: { background: "#C8A96E", color: "#0c0c0c", border: "none", borderRadius: 2, padding: "12px 22px", fontSize: 11, letterSpacing: "0.1em", textTransform: "uppercase", cursor: "pointer", fontFamily: "inherit", fontWeight: 700, transition: "opacity 0.2s", display: "block", width: "100%" },
  ghostBtn: { background: "transparent", color: "#4a4540", border: "1px solid #1a1a1a", borderRadius: 2, padding: "10px 18px", fontSize: 11, letterSpacing: "0.07em", cursor: "pointer", fontFamily: "inherit" },
  backBtn: { background: "none", border: "none", color: "#3a3530", cursor: "pointer", fontSize: 12, fontFamily: "inherit", padding: "0 0 16px", display: "block", letterSpacing: "0.05em", textAlign: "left" },
  savedBadge: { fontSize: 11, color: "#7EB8A4", textAlign: "center", letterSpacing: "0.08em", padding: "9px 0" },
  emptyState: { fontSize: 12, color: "#2a2520", fontStyle: "italic", textAlign: "center", padding: "24px 0", lineHeight: 1.6 },
};