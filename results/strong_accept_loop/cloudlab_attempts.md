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
- Scientific status: no inference result yet.

The generated request source was checked in the portal before submission and contained both `<hardware_type name="c240g5"/>` and the Ubuntu 22.04 image URN.
