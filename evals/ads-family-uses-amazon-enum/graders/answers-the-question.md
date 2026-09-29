---
type: llm
---

PASS if the reply tells the user which Sponsored Brands budget rule(s) exist, as a
final, usable answer (mentioning that it retried after an internal rename notice is
fine — that is honest, not a failure).
FAIL if the reply gives up, shows a raw error or stack trace as its final answer, or
never states which budget rules exist.
