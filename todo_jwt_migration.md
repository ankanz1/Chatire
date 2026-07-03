Unique Feature Todo — Differentiators vs WhatsApp/Telegram

Only what makes this app stand out. Core plumbing (auth, messaging, notifications) assumed already covered in the main build roadmap.

Trust & Ownership


 [x] No phone number required — signup via email/username only
 [ ] End-to-end encryption ON by default for all 1:1 and group chats (not opt-in like Telegram)
 [ ] Clear "we can't read your messages" explainer in onboarding (builds trust, differentiates from WhatsApp/Meta)
 [ ] No ad tracking / no data resale — state this explicitly in-app, not just in a privacy policy


Interaction Model


 Threaded replies as the default group chat UX (not flat scroll like WhatsApp)
 "Read when ready" status option — user can hide read receipts without disabling them for others (asymmetric control WhatsApp doesn't offer)
 Per-chat disappearing messages with custom expiry (not just Telegram's fixed presets)
 Voice message auto-transcription, shown as skimmable text before playback


AI-Native Layer (the biggest differentiator)


 In-thread "Ask AI" — summon an AI assistant inside any conversation, visible to participants who opt in
 Thread summarization — TL;DR button on long/missed threads
 Live translation toggle per chat (inline, not a separate screen)
 Smart reply suggestions drafted contextually from the thread
 Design note: AI features need plaintext access to the message — build an explicit per-chat opt-in so it doesn't silently break E2E guarantees


Group/Community Specific


 Mute mentions-only vs mute everything (granular, not binary like most apps)
 Lightweight polls/decisions embedded in threads (no separate app needed)


Nice-to-Have Differentiators (lower priority)


 Local/offline-first sync (works fully without internet, syncs when back online)
 Community-run/open-source governance messaging in-app (if going that route)


Not Unique — Skip Overbuilding


 [x] Reactions, stickers, GIFs, basic read receipts — table stakes, don't over-invest early
