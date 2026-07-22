# CloudLab Experiment Attempts

All timestamps below are portal timestamps on 2026-07-22. A failed allocation is infrastructure evidence only and is not experimental evidence.

## Attempt 1: unavailable d7525

- Project / experiment: `cbnu-ai-lab/lad-phi35-pilot`
- Experiment UUID: `eaf355ca-ca95-462c-9e32-94664f24d58a`
- Profile: `small-lan:43`
- Requested site/type: Wisconsin `d7525`
- Requested image: Ubuntu 22.04
- Duration: 16 hours
- Portal result: `failed`
- Mapper message: one `d7525` requested and zero available because of existing reservations.
- Scientific status: no node provisioned, no model downloaded, and no inference run.

## Availability observation and hardware pivot

The authenticated Resource Availability page showed the following Wisconsin counts during the retry: `c220g1=3`, `c220g2=23`, `c220g5=32`, `c240g5=3`, `d7525=0`, and `sm110p=2`. The official CloudLab hardware manual identifies `c240g5` as a 20-core Skylake node with 192 GB RAM and one NVIDIA Tesla P100 12 GB GPU. The pilot therefore pivots from the unavailable A30 node to an available P100 node and changes inference dtype from `bfloat16` to `float16`. This hardware change affects runtime comparisons and will be recorded with the run; it does not change the paired intervention.

Official hardware source: <https://docs.cloudlab.us/hardware.html>

## Attempt 2: dedicated c240g5 profile

- Project / experiment: `cbnu-ai-lab/lad-phi35-p100`
- Experiment UUID: `d8ddb58f-045b-409e-8c4e-0704055f2546`
- Profile: `cbnu-ai-lab/lad-c240g5-pilot:0`
- Profile UUID: `f524dd0b-887b-4118-bccb-dcc16486630e`
- Local RSpec: `cloudlab/lad-c240g5.rspec`
- Requested site/type: Wisconsin `c240g5`
- Requested image: `UBUNTU22-64-STD`
- Duration: 16 hours
- Last observed portal state: `ready`
- Assigned node: `c240g5-110121`
- SSH hostname: `c240g5-110121.wisc.cloudlab.us`
- SSH identity prepared locally: `C:\Users\netdb\.ssh\cloudlab_ed25519` (private key contents are not copied into the repository)
- Driver preparation: the base image exposed the P100 through PCI but had only `nouveau`; Ubuntu `ubuntu-drivers devices` recommended `nvidia-driver-535`. Version `535.309.01-0ubuntu0.22.04.1` was installed and verified after reboot.
- Verified runtime: NVIDIA driver `535.309.01`, reported CUDA compatibility `12.2`, Tesla P100-PCIE-12GB, 12,288 MiB VRAM.
- PyTorch runtime: `torch==2.5.1+cu121`, CUDA available, compute capability `(6, 0)`.
- Scientific status: the first compatibility-fixed 50-item inference completed, but its high strict-format parse-failure rate prevents promotion to evidence.

The generated request source was checked in the portal before submission and contained both `<hardware_type name="c240g5"/>` and the Ubuntu 22.04 image URN.

### Attempt 2a: dependency incompatibility, retained as diagnostic evidence

The first real invocation at Git commit `344a58a` downloaded and loaded the pinned model but failed on its first generation. The unbounded requirements file had selected `transformers==5.14.1`; the pinned Phi-3.5 remote code accessed `DynamicCache.seen_tokens`, which that version no longer exposes. No paired result was produced, and this attempt is not scientific evidence. The failure trace remains in the CloudLab run log.

The official Phi-3.5 model card specifies `transformers==4.43.0` and `accelerate==0.31.0`. Those versions were pinned instead of patching third-party cache code. A one-item smoke test then completed one private generation and both paired conditions with zero parser failures. The parser regression discovered by this smoke test—Phi-3.5 returned `<answer>E) option text</answer>` rather than only `E`—is covered by a unit test and a candidate-bounded normalization rule.

### Attempt 2b: compatibility-fixed full pilot

- Git commit: `0462b68`
- Output path: `results/runs/phi35-pilot-ce1b110/` (the directory label records the substantive compatibility-fix commit; `run-git-commit.txt` records the exact execution commit)
- Model stack: `torch==2.5.1+cu121`, `transformers==4.43.0`, `accelerate==0.31.0`
- Dtype: `float16`
- Seed: `1701`
- Completed records: 50 private answers; 26 parseable private answers yielded 52 paired revision generations
- Strict-format baseline parse-failure rate: `0.48`
- Candidate result: harmful COMMON-minus-INDEPENDENT difference `0.0`; beneficial difference `+0.1333` with bootstrap interval `[0.0, 0.3333]`
- Current state: complete but not promoted; artifacts remain `empirical-candidate-unverified`

Raw-output inspection showed that most strict-format failures contained an unambiguous candidate label either immediately after an opening `<answer>` tag whose closing tag was truncated, or at the first response position without tags. A candidate-bounded parser change accepts only those leading labels; it does not search later reasoning text. Two regression tests lock those cases. Because the omitted private answers never received paired revisions, metrics cannot be repaired by post-hoc re-parsing alone: a distinct full rerun is required and will retain Attempt 2b unchanged.

### Attempt 2c: bounded-parser full rerun

- Git commit: `e53721e`
- Output path: `results/runs/phi35-pilot-e53721e/`
- Status: complete; strengthened integrity validator `pass`
- Completed records: 50 private answers plus 100 paired revision generations
- Baseline parse-failure rate: `0.0`
- Baseline accuracy: `0.44`
- Harmful revision COMMON-minus-INDEPENDENT: `-0.04545`, paired bootstrap interval `[-0.13636, 0.0]`, eligible `n=22`
- Beneficial revision COMMON-minus-INDEPENDENT: `+0.07143`, paired bootstrap interval `[0.0, 0.17857]`, eligible `n=28`
- Stop rule: complete all eligible paired generations; do not inspect effects for optional stopping

The result does not support the anticipated direction that independent lineage should reduce harmful revision or increase beneficial revision. Both intervals include zero at an endpoint, and the point estimates weakly favor COMMON lineage on these outcomes. This bounded one-model, one-task pilot is retained as a negative/mixed result and does not support C1–C3.
