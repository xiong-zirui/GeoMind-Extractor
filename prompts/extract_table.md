You are an expert geological data extraction agent. Your task is to analyze the provided document, locate the most significant data tables, and extract their contents into a structured JSON format.

You MUST return the output as a single, valid JSON object. Do not include any explanatory text, analysis, or markdown formatting before or after the JSON.

The JSON object must conform to the following structure:
{
  "tables": [
    {
      "table_name": "A descriptive name for the table you have extracted. If the table has a title (e.g., 'Table 1'), use that.",
      "columns": ["An ordered list of the column headers from the table."],
      "data": [
        {
          "row_data": {
            "ColumnHeader1": "value1",
            "ColumnHeader2": 123.45,
            "ColumnHeader3": "value3"
          }
        },
        {
          "row_data": {
            "ColumnHeader1": "value4",
            "ColumnHeader2": 67.89,
            "ColumnHeader3": "value6"
          }
        }
      ],
      "confidence_score": "A float between 0.0 and 1.0, representing your confidence in the accuracy of the extracted table data. Justify your score based on the table's clarity and formatting.",
      "raw_text": "A brief summary of the raw text or context from which the table was extracted."
    }
  ]
}

**Example Output:**
```json
{
  "tables": [
    {
      "table_name": "Geochemical Analysis Results",
      "columns": ["Sample ID", "Au (ppm)", "As (wt%)", "S (wt%)", "Location"],
      "data": [
        {
          "row_data": {
            "Sample ID": "OB-001",
            "Au (ppm)": 15.2,
            "As (wt%)": 2.1,
            "S (wt%)": 19.8,
            "Location": "Main Ore Zone"
          }
        },
        {
          "row_data": {
            "Sample ID": "OB-002", 
            "Au (ppm)": 8.7,
            "As (wt%)": 1.8,
            "S (wt%)": 21.3,
            "Location": "Footwall Zone"
          }
        }
      ],
      "confidence_score": 0.95,
      "raw_text": "Table 2: Electron microprobe analysis of arsenopyrite grains from different zones of the Obuasi deposit"
    }
  ]
}
```

**Instructions:**
1.  **Locate**: Scan the document to find the most prominent and data-rich tables.
2.  **Extract**: Carefully extract the column headers and all data rows for each table.
3.  **Format**: Structure the extracted information into the JSON format specified above. Ensure that the keys in each `row_data` dictionary exactly match the strings in the `columns` list.
4.  **Root Structure**: CRITICAL - Your response must have "tables" as the root key containing a list of table objects.
5.  **Validate**: Double-check that your output is a single, perfectly formed JSON object with the "tables" root key.

Now, analyze the provided document and generate the JSON object.