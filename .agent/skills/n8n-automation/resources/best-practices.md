# n8n Best Practices & Tool deep-dive

## Expression Syntax
- **Correct Pattern**: `{{ $json.body.field }}`
- **Common Gotcha**: Webhook trigger data is nested under `.body`.
- **Avoid**: Expressions inside Code nodes (use JS/Python variables instead).

## Production Tier Guide
| Feature | Tier 1 (Internal) | Tier 2 (Production) | Tier 3 (High-Value) |
| :--- | :--- | :--- | :--- |
| **Error Handling** | None | Try/Catch + Notify | Rollback + Audit Log |
| **Validation** | Basic | Input Schema Check | Idempotency Keys |
| **Logging** | n8n Logs | External DB (Postgres) | Compliance SIEM |

## Mandatory Checklist
- [ ] Pattern identified?
- [ ] `$json.body` used for webhooks?
- [ ] `validate_workflow` passed?
- [ ] Hardening tier selected?
- [ ] Credentials secured?
