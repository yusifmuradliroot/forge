# RULES — hard rules for AI (forge, private)

1. **Pass contract.** Every pass lives in `src/passes/<name>.py`, exposes `run(code: str) -> str`,
   never crashes on valid JS, never alters runtime behavior (only representation).
2. **VERSION discipline.** Bump `VERSION` on every behavior change. Forgetting is a defect.
3. **Two targets.** Tool code runs on dev machine (python3, any OS). Emitted JS MUST run on
   Firefox-based browsers + Violentmonkey. Test fixtures under `tests/`.
4. **Small steps.** One decision, one change, one commit per agreed step.
5. **No code without approval.** Discuss the plan first, write code only after user says so.
6. **Language.** User communication in Turkish. Code comments in English. Keep both short.
7. **No rambling.** Short, direct answers. One decision per message.
8. **Verify.** Run `tools/forge.py` on fixtures after every pass change. Report commit hashes.
9. **AI annotation fully allowed.** Notes may live in code too — but never credentials/tokens in git.
10. **Prune against bloat.** Keep `AI/` files short; propose before destructive cleanup.
11. **Context cues.** Record mode switches in `WHEREWEARE.md` under "User context":
    - "konsol erişimim yok" → mobile: visual-feedback diagnosis only.
    - "konsol erişimim var" → desktop: console logs may be used.
12. **Two-repo sync — only when needed.** Shared contracts (pass API, checker logic, conventions)
    stay aligned with abyss/grimorium tooling. Repo-specific files never cross repos.
