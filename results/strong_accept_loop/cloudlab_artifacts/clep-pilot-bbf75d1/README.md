# CLEP protocol-v1 CloudLab artifact

Execution commit: `bbf75d1c8a5d83353f832b0083a722721dfc1ea6`.

This directory contains 72 raw generations: two pinned open-model families, three prompt methods, 12 parallel items per cell. All six independent integrity reports are `fail` because the predeclared exact typed-output parser encountered failures. The proposition scorer also required a canonical lemma while the prompt permitted free-form proposition text, making all-fields exact match structurally unsuitable. These artifacts are diagnostic only and support no CLEP headline claim.

Protocol v1 will not be rescored with a relaxed parser. A later protocol may replace free-form proposition text with predeclared categorical fields, but it must use new generations and a new versioned artifact directory.
