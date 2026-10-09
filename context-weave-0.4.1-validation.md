# Runtime validation

Local synthetic tests only. No official 0.4.1 score or Full result is claimed.

- 71 regression tests passed, including spawned-process hard hangs, cooperative timeouts, active/queued cancellation, client disconnects, bounded queues, queue-inclusive deadlines, crash and idle-crash recovery, shutdown cleanup, EOS accounting and single/batch HTTP validation.
- Initial five-minute real-model pilot: 89 successful requests in 301.61 seconds, no failures/restarts, identical fixed-anchor outputs. Post-request allocated memory stayed at 8029.99 MiB; reserved at 8032.0 MiB. The end/start anchor median ratio was 0.8973.
- Actual client disconnect recovery: 0.625 seconds, temporary GPU memory returned to baseline. Deliberately terminating the real model worker triggered automatic reload and a successful fresh response after 19.156 seconds. These intentional faults are separate from the soak test.
- Full local Add/Search path: two concurrent 16-chunk synthetic Adds, Bailian embedding, idempotent retry, original-source integrity and user isolation passed in 55.031 seconds. This is not an apples-to-apples speed comparison with the baseline's earlier run.
- Sustained test: **passed**, 5123 requests over 14400.8 seconds of the requested 14400.0 seconds. See VALIDATION.json for acceptance metrics. A running test is not a pass.

Memory values describe PyTorch tensors and its caching allocator, not all GPU usage shown by Windows/nvidia-smi. Fixed synthetic anchors help detect degradation, but do not measure retrieval quality or guarantee multi-day Full reliability. Timings depend on this RTX 5070 Ti Laptop GPU and concurrent desktop load.
