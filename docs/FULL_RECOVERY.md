# Full0.32.0 recovery and version-consistency disclosure

Original Full job:`teval_6c99618ea0916224`. The participant authorized repair/resume on2026-10-15. The same task was resumed; the repair did not create a new Full. The original source/archive and the final recovery archive are both preserved. The original fixed commit is e84af580a3a9a21f1eab6328d41e8b93bb52552e; the terminal Full source is the separately identified recovery snapshot.

The current public frozen tree at `releases/sourcetrail-0.32.0-full/` and the recovery archive already contain the repaired terminal Full implementation. The comparison below records historical changes from the original 0.32 archive.

Prior logs recorded72 upstream400responses without categories. The historical root cause cannot be fully reconstructed from those logs. Synthetic tests reproduced the provider's input-length rejection for a very long query. This does **not** prove all earlier400responses had the same cause.

Compared byte-for-byte with the original0.32archive, exactly three files changed or were added:

* `adaptive_evidence/remote_encoder.py`: recognizes the provider's input-length rejection, divides failed batches to isolate the rejected item, splits that item on UTF-8 codepoint boundaries into segments of at most7,680bytes, retains all text, embeds with the same model/dimensions/endpoint/role/normalization, pools segment unit vectors by UTF-8 byte length, then normalizes. Whitespace segments attach to adjacent text. Successful normal requests keep the original path; unrelated errors fail closed.
* `adaptive_evidence/api.py`: adds a health marker identifying the recovery behavior.
* `tests/test_embedding_length_recovery.py`: adds seven synthetic regression checks. Total historical suite71passed.

No model replacement, generative LLM, query truncation, database rebuild, namespace change or request-id reset was introduced. Core retrieval and the original private profile remained unchanged at Full completion. However, the repaired adapter **changes previously rejected long-input behavior** and is not equivalent to a hypothetical unlimited-context embedding. It may add provider calls and cannot be described as purely metadata or as byte-identical to the originally submitted implementation.

Historical synthetic checks included short-vector equality, original-adapter database compatibility, an810,000-character query producing a normalized1,024-dimensional vector via106segments, and an isolated live Add/Search contract preflight. These are not official score improvement evidence.

The organizer's current rules require version consistency and review of Full anomalies. The task's successful state does not by itself prove the recovery was accepted for publication. Provide this disclosure, the job ID, original commit, final archive hashes and deployment identity for organizer review. No written approval is asserted here.

Provider reference: [Alibaba Cloud synchronous text embedding API](https://www.alibabacloud.com/help/en/model-studio/text-embedding-synchronous-api). Method references through0.32remain in the frozen PROVENANCE.md. No upstream source or benchmark answer was added by this repair.
