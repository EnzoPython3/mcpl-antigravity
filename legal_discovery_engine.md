# Technical Spec: Local-First Legal Discovery Engine

**Project:** Automated Client Intake & Case Preparation System
**Objective:** Reduce the manual load on 22 support staff by automating the ingestion, analysis, and preparation of legal discovery files.
**Infrastructure:** n8n (Self-Hosted), Local LLM (Ollama/Llama 3 on M3 Pro), Local File Storage.

---

## 1. System Architecture

### A. The Ingestion Layer (The Funnel)
*   **Input Channels:**
    *   **Secure Web Portal:** Client uploads documents directly (forms, bank statements, IDs).
    *   **Email Watch:** Dedicated inbox (`newcases@firm.com`) monitored by n8n IMAP node.
    *   **Internal Drop Folder:** Network drive folder where paralegals dump "raw" client files.
*   **Action:** n8n triggers on new file -> Creates a unique `Case_ID` folder structure.

### B. The Processing Layer (The "Grinder")
*   **Format Normalization:** Convert images (JPG/PNG) to PDF.
*   **OCR (Optical Character Recognition):**
    *   *Tool:* `Tesseract` (via n8n Execute Command) or a local Vision Model (e.g., `Llava` via Ollama) for describing images.
    *   *Goal:* Turn every scanned affidavit and bank statement into searchable text.
*   **PII Redaction (Optional but recommended):** Regex-based pre-processing to identify SSNs/ID numbers for security flags.

### C. The Intelligence Layer (The "Brain") - **CRITICAL**
*   **Engine:** Local LLM (Llama 3 8B or Mistral 7B) running via Ollama on M3 Pro.
*   **Task 1: Classification:**
    *   *Prompt:* "Analyze this text. Is it a Bank Statement, Affidavit, Marriage Certificate, or Police Report? Output JSON."
*   **Task 2: Extraction (The "Golden Data"):**
    *   *Prompt:* "Extract the following entities: Client Name, Opposing Party, Date of Marriage, Date of Separation, List of Assets > $10k, Allegations of Abuse (Yes/No)."
*   **Task 3: Timeline Construction:**
    *   *Prompt:* "Create a chronological list of events based on the dates found in these affidavits."

### D. The Output Layer (The "Brief")
*   **Asset Schedule:** Auto-fill a spreadsheet with assets found in financial docs.
*   **Case Summary:** A 2-page PDF summary generated from the LLM's analysis.
*   **Assignment Logic:**
    *   *Rules:* If "Assets > $5M" -> Assign to Senior Partner. If "Contested Custody" -> Assign to Family Specialist.
*   **Notification:** Email to the assigned Attorney with the "Court Ready" packet attached.

---

## 2. Implementation Steps (MVP)

1.  **Setup Ollama:** Ensure Llama 3 (or a fine-tuned legal model) is running and accessible via API on your local network.
2.  **The "Intake" Workflow:** Build the n8n workflow that simply watches a folder, OCRs the PDF, and saves the text to a `.txt` file.
3.  **The "Analysis" Workflow:** Build the n8n node that reads that `.txt` file, sends it to Ollama with a strict System Prompt, and parses the JSON response.
4.  **The "Report" Workflow:** Map the JSON data into a predefined Word/PDF template.

---

## 3. Security & Compliance
*   **Zero Data Egress:** Ensure the n8n instance and Ollama API have **NO** internet access for the processing nodes. All data stays on the local metal.
*   **Audit Logs:** n8n must log every file touched and every decision made for accountability.
