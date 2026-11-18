# Known Limitations & Boundary Constraints

**Document Reference:** LIM-RET-2026-V1  
**Project:** AI-Powered Smart Business Operations & Decision Intelligence System  
**Dataset:** `03_Retail.xlsx` (Synthetic Demonstration Dataset)  
**Policy:** Strict Transparency & Non-Fabrication  

---

## 1. Dataset Boundary Limitations

1. **Absence of Clickstream / Web Traffic Analytics**:
   - The dataset records point-of-sale transactions and fulfillment channels (`In-store`, `Online`, `Mobile App`), but does not track web visits, click events, cart additions, or bounce rates.
   - *System Boundary:* Conversion funnel analysis is restricted to transaction completion rates (`Completed` vs `Cancelled` vs `Returned`).
2. **Channel-Specific Marketing Attribution**:
   - Operating expense records categorize marketing spend by physical branch location (`store_id`), not by digital campaign (e.g., Google Ads vs Meta Ads vs SEO).
   - *System Boundary:* Customer Acquisition Cost (CAC) per advertising channel cannot be deterministically computed and is not fabricated.
3. **No Direct Customer Sentiment / Product Reviews**:
   - Customer records contain segment classifications and transactions contain return statuses, but no text reviews, 5-star ratings, or Net Promoter Score (NPS) fields exist.
   - *System Boundary:* Quality issues are deduced from product return frequencies rather than subjective feedback.
4. **Synthetic Nature of Dataset**:
   - The provided data is synthetic demonstration data generated for academic and technical evaluation purposes. All customer names, email addresses, and phone references are fictional.

---

## 2. Infrastructure & Technical Boundaries

1. **Cold Starts on Free Cloud Tiers**:
   - When deployed on Render free web service tiers, the backend service may spin down after 15 minutes of inactivity, resulting in a 30-50 second latency on the first request.
2. **LLM Quota & Rate Limiting**:
   - When using Google Gemini free tier API keys, calls may be rate-limited to 15 requests per minute. The system features a fallback mechanism ensuring zero crashes and 100% verified analytical outputs even if quotas are temporarily exhausted.
3. **In-Memory Browser Charts**:
   - Recharts visualizes client-side data; rendering datasets with over 50,000 raw points on lower-end mobile devices can cause UI latency. The platform resolves this by serving aggregated KPI endpoints rather than raw transactional dumps.
