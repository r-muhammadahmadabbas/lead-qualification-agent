# Monitoring Checklist — Web3Geeks Client Inquiry API

## What to Track in Production

### 1. Error Rate
- **Metric:** Percentage of requests that return errors
- **Alert Threshold:** > 5% error rate
- **Re-evaluation:** Weekly
- **Action:** If threshold exceeded, check logs for root cause

### 2. Cost Drift
- **Metric:** Average cost per request over time
- **Alert Threshold:** > 20% increase from baseline
- **Re-evaluation:** Weekly
- **Action:** Review LLM usage, check for unusual patterns

### 3. Latency
- **Metric:** Average response time per request
- **Alert Threshold:** > 5 seconds average
- **Re-evaluation:** Daily
- **Action:** Check LLM provider latency, optimize prompts

### 4. Output Quality
- **Metric:** Average quality score (manual sampling)
- **Alert Threshold:** < 4/5 average score
- **Re-evaluation:** Monthly
- **Action:** Review prompts, update training data

### 5. Token Usage
- **Metric:** Average tokens per request
- **Alert Threshold:** > 10,000 tokens per request
- **Re-evaluation:** Daily
- **Action:** Optimize prompts, reduce context length

### 6. Human Override Rate
- **Metric:** Percentage of responses modified by humans
- **Alert Threshold:** > 10% override rate
- **Re-evaluation:** Weekly
- **Action:** Review agent decisions, update qualification logic

## Monitoring Dashboard

| Metric | Current | Threshold | Status |
|--------|---------|-----------|--------|
| Error Rate | 0% | < 5% | OK |
| Cost per Request | $0.002 | < $0.005 | OK |
| Avg Latency | 8.5s | < 5s | WARNING |
| Quality Score | 4.5/5 | > 4/5 | OK |
| Token Usage | 500 | < 10,000 | OK |
| Override Rate | 0% | < 10% | OK |

## Logging Format

```
2024-01-15 10:30:00 - INFO - Request received: INQ-001 from john@techcorp.com
2024-01-15 10:30:05 - INFO - Validation passed: INQ-001
2024-01-15 10:30:06 - INFO - Company found: TechCorp Solutions
2024-01-15 10:30:07 - INFO - Lead qualified: high (score=6)
2024-01-15 10:30:12 - INFO - Response drafted: INQ-001
2024-01-15 10:30:12 - INFO - Request completed: INQ-001 - Status: approved - Latency: 12.00s
```

## Re-evaluation Cadence

| Task | Frequency | Owner |
|------|-----------|-------|
| Review error logs | Daily | Engineering |
| Check cost trends | Weekly | Finance |
| Sample quality review | Monthly | Product |
| Update qualification logic | Quarterly | Product |
| Review monitoring thresholds | Quarterly | Engineering |
