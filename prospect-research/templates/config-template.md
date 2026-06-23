# prospect-research config

Copy this file to `prospect-research/config.md` and fill in your details before first use.
Claude reads this file at the start of every research session.

---

## Your ICP (Ideal Customer Profile)

Describe your ideal customer. Be specific — the more precise this is, the sharper the research.

```
Industry:        [e.g. asset management, legal, healthcare, SaaS]
Role / seniority: [e.g. portfolio manager, general counsel, VP Operations]
Company size:    [e.g. 10–200 employees, $10M–$500M AUM]
Geography:       [e.g. France, EU, North America]
Core problem:    [e.g. manual reporting, fragmented data, slow compliance review]
Out-of-ICP:      [who you explicitly do NOT serve — helps skip quickly]
```

## Your product / service

```
Name:           [your product or service name]
One-liner:      [what it does in one sentence]
Key differentiator: [what makes it different from generic alternatives]
Proof points:   [metrics, case studies, or outcomes you can cite — e.g. "saves 3h/day"]
```

## Outreach angle framework

Customize V1/V2/V3 for your offer. These are the three angles Claude will draft for every prospect.

```
V1 — Workflow pain:
  [The specific manual / time-consuming task your product removes.
   Example: "copy-paste between Bloomberg and Excel for morning reports"]

V2 — Peer / expertise angle:
  [A practitioner-to-practitioner hook — you understand their world, not just their job title.
   Example: "from one quant PM to another — the part of your stack that still doesn't scale"]

V3 — External signal hook:
  [A rebound off a market event, regulation, or industry news.
   Example: "with the new DORA deadline, firms are auditing their data pipelines — we can shortcut that"]
```

## Vault directory

```
vault_dir: ~/your-vault    # absolute path to your local Obsidian vault or notes folder
                            # Capsules land in {vault_dir}/Capsules/{slug}.md
                            # Daily logs land in {vault_dir}/Daily/{YYYY-MM-DD}.md
```

## CRM (optional)

```
crm_notes_field: Notes     # the CRM field name for the short projection (≤200 chars)
crm_url_field:   CapsuleURL  # field to store the local vault link (leave blank to skip)
```
