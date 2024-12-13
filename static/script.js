// Define the function at the global scope
function cleanAndFormatText(text) {
    // Remove markdown formatting
    text = text.replace(/\*\*AI Assistant Summary\*\*/g, '');
    text = text.replace(/\*\*/g, '');

    // Process text line by line
    const lines = text.split('\n');
    let formattedLines = [];
    let indentLevel = 0;

    lines.forEach(line => {
        line = line.trim();
        if (!line) return;

        // Handle section headers
        if (line.startsWith('OVERVIEW') || line.startsWith('DETAILS') || line.startsWith('CONCLUSION')) {
            formattedLines.push('\n' + line + '\n');
            indentLevel = 0;
            return;
        }

        // Check for main topics
        if (line.includes(': -') || line.endsWith(':')) {
            indentLevel = 0;
            formattedLines.push('\n' + line);
            indentLevel++;
            return;
        }

        // Handle bullet points
        if (line.startsWith('-')) {
            let content = line.substring(1).trim();
            // Add proper indentation
            let indent = '    '.repeat(indentLevel);
            formattedLines.push(indent + '• ' + content);
            return;
        }

        // Regular text
        formattedLines.push(line);
    });

    // Join lines and add proper spacing
    let formattedText = formattedLines.join('\n');

    // Clean up excessive newlines
    formattedText = formattedText.replace(/\n{3,}/g, '\n\n');

    return formattedText;
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded - Initializing script...');

    // Get all form elements
    const queryForm = document.getElementById('query-form');
    console.log('Query form found:', queryForm);

    const queryInput = document.getElementById('query');
    const confidenceInput = document.getElementById('confidence-threshold');
    const relevanceInput = document.getElementById('relevance-threshold');
    const enableDateRange = document.getElementById('enable-date-range');
    const dateRangeInputs = document.getElementById('date-range-inputs');
    const loadingIndicator = document.getElementById('loading-indicator');
    const resultsContainer = document.getElementById('results-container');
    const llmResponse = document.getElementById('llm-response');
    const llmContent = document.getElementById('llm-content');
    const docsTable = document.getElementById('docs-table');
    const docsTableBody = document.getElementById('docs-table-body');
    const queryHistoryDropdown = document.getElementById('query-history-dropdown');

    // Verify all elements are found
    console.log('All form elements found:', {
        queryInput,
        confidenceInput,
        relevanceInput,
        enableDateRange,
        dateRangeInputs,
        loadingIndicator,
        llmResponse,
        llmContent,
        docsTable,
        docsTableBody
    });

    // Date range toggle handler
    enableDateRange.addEventListener('change', () => {
        dateRangeInputs.style.display = enableDateRange.checked ? 'block' : 'none';
    });

    // Query history dropdown handler
    queryHistoryDropdown.addEventListener('change', () => {
        const selectedQuery = queryHistoryDropdown.value;
        if (selectedQuery) {
            queryInput.value = selectedQuery;
            queryInput.style.height = 'auto';
            queryInput.style.height = queryInput.scrollHeight + 'px';
        }
    });

    // Form submit handler
    queryForm.addEventListener('submit', async (e) => {
        console.log('Form submission started');
        e.preventDefault();
        console.log('Default form submission prevented');

        // Show loading indicator
        loadingIndicator.style.display = 'flex';
        console.log('Loading indicator shown');

        // Get form values
        const queryValue = queryInput.value.trim();
        const confidenceValue = confidenceInput.value.trim();
        const relevanceValue = relevanceInput.value.trim();
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;

        console.log('Form values collected:', {
            query: queryValue,
            confidence: confidenceValue,
            relevance: relevanceValue,
            startDate,
            endDate
        });

        // Prepare payload
        const payload = { query: queryValue };
        if (confidenceValue) payload.confidence_threshold = confidenceValue;
        if (relevanceValue) payload.relevance_threshold = relevanceValue;
        if (enableDateRange.checked) {
            if (startDate) payload.start_date = startDate;
            if (endDate) payload.end_date = endDate;
        }

        console.log('Sending payload to server:', payload);

        try {
            console.log('Making fetch request to /query');
            const response = await fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            console.log('Response received:', response);
            loadingIndicator.style.display = 'none';

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Query failed');
            }

            const data = await response.json();
            console.log('Data received from server:', data);

            // Clear previous results
            resultsContainer.innerHTML = "";

            if (data.answer) {
                llmContent.innerHTML = cleanAndFormatText(data.answer);
                llmResponse.style.display = 'block';
                console.log('Answer displayed');
            } else {
                llmResponse.style.display = 'none';
                console.log('No answer received');
            }

            // Update documents table
            if (data.relevant_documents?.length > 0) {
                docsTableBody.innerHTML = "";
                data.relevant_documents.forEach(doc => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${doc.title}</td>
                        <td>${doc.author}</td>
                        <td>${doc.confidence}</td>
                        <td>${doc.relevance}</td>
                    `;
                    docsTableBody.appendChild(row);
                });
                docsTable.style.display = 'table';
                console.log('Documents table updated');
            } else {
                docsTable.style.display = 'none';
                console.log('No relevant documents');
            }

        } catch (error) {
            console.error('Error during query:', error);
            loadingIndicator.style.display = 'none';
            resultsContainer.innerHTML = `<p class="error">Error: ${error.message}</p>`;
            llmResponse.style.display = 'none';
            docsTable.style.display = 'none';
        }
    });

    // Upload form handling
    const uploadForm = document.getElementById('upload-form');
    const uploadMessage = document.getElementById('upload-message');

    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const fileInput = document.getElementById('file');
        if (!fileInput.files.length) {
            uploadMessage.textContent = "Please select a file.";
            return;
        }

        loadingIndicator.style.display = 'flex';

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            loadingIndicator.style.display = 'none';

            const data = await response.json();
            if (response.ok) {
                uploadMessage.textContent = data.message;
            } else {
                uploadMessage.textContent = `Error: ${data.error}`;
            }
        } catch (error) {
            loadingIndicator.style.display = 'none';
            uploadMessage.textContent = `Unexpected error: ${error}`;
        }
    });

    function updateQueryHistory(history) {
        // Clear existing options except the first "Select..." option
        for (let i = queryHistoryDropdown.options.length - 1; i > 0; i--) {
            queryHistoryDropdown.remove(i);
        }

        // Add past queries as options to the dropdown
        history.forEach(entry => {
            const option = document.createElement('option');
            option.value = entry.query;
            option.textContent = entry.query;
            queryHistoryDropdown.appendChild(option);
        });
    }
});