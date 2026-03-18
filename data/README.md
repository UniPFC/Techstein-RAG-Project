# Auto-Ingestion Data Folder

Any spreadsheet files placed in this folder will be automatically detected by the API on startup.
Each file will become a **Public Chat Type** available to all users.

## How it works

1.  **File Naming**: The file name determines the Chat Type name and description.
    *   **Format**: `Title --- Description.xlsx`
    *   **Example**: `Finance 2024 --- Financial Report for Q1.xlsx`
        *   **Chat Name**: "Finance 2024"
        *   **Description**: "Financial Report for Q1"
    *   **Fallback**: If you don't use `---`, the filename is used as the title and a default description is generated.
        *   `HR-Policies.csv` -> **"Hr Policies"**

2.  **Automatic Creation**:  
    *   If a Chat Type with that name doesn't exist, it is created automatically.
    *   The collection in Qdrant is created.
    *   The file content is ingested.

3.  **Updates**:
    *   If the Chat Type already exists and has data, the file is skipped (to avoid duplicates).
    *   To update a knowledge base: Delete the Chat Type via the API/Frontend, then restart the API. It will re-read the file and re-ingest.

## Supported Formats

*   `.xlsx` (Excel)
*   `.xls` (Legacy Excel)
*   `.csv` (Comma Separated Values)

**Required Columns:** `question`, `answer`
