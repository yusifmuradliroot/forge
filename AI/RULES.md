# RULES — hard rules for AI (forge, private)

1. **Pass contract.** `src/passes/<name>.py`, `run(code: str) -> str`. Pure, no I/O.
   Never crashes on valid JS. Never changes runtime behavior — only representation.
2. **Minimalism.** Output stays small: strip notes, short names, zero decoys, zero fake
   content, zero dead code. Protection comes from the transform, never from noise.
3. **VERSION discipline.** Bump `VERSION` on every behavior change. Forgetting is a defect.
4. **Two targets.** Tool runs on dev machine (python3). Output runs on Firefox + Violentmonkey.
   Verify every change with fixtures AND `node --check` on a real file.
5. **Small steps.** One decision, one change, one commit per agreed step.
6. **No code without approval.** Discuss the plan first, write code only after user says so.
7. **Language.** User communication in Turkish. Code comments in English. Keep both short.
8. **No rambling.** Short, direct answers. One decision per message.
9. **Verify.** Run the full chain on the biggest real file before calling a pass done.
   Report commit hashes after push.
10. **AI annotation fully allowed.** Notes may live in code too — but never credentials/tokens in git.
11. **Prune against bloat.** Keep `AI/` files short; propose before destructive cleanup.
12. **Context cues.** Record mode switches in `WHEREWEARE.md` under "User context":
    - "konsol erişimim yok" → mobile: visual-feedback diagnosis only.
    - "konsol erişimim var" → desktop: console logs may be used.
13. **Two-repo sync — only when needed.** Shared contracts stay aligned with abyss/grimorium
    tooling. Repo-specific files never cross repos.
14. **Open-source hygiene.** Original code only, zero dependencies — relicense option stays open.
