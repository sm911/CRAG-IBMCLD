// Define the function at the global scope
function cleanAndFormatText(text) {
    // Existing cleanAndFormatText function remains unchanged
    text = text.replace(/\*\*AI Assistant Summary\*\*/g, '');
    text = text.replace(/\*\*/g, '');

    const lines = text.split('\n');
    let formattedLines = [];
    let indentLevel = 0;

    lines.forEach(line => {
        line = line.trim();
        if (!line) return;

        if (line.startsWith('OVERVIEW') || line.startsWith('DETAILS') || line.startsWith('CONCLUSION')) {
            formattedLines.push('\n' + line + '\n');
            indentLevel = 0;
            return;
        }

        if (line.includes(': -') || line.endsWith(':')) {
            indentLevel = 0;
            formattedLines.push('\n' + line);
            indentLevel++;
            return;
        }

        if (line.startsWith('-')) {
            let content = line.substring(1).trim();
            let indent = '    '.repeat(indentLevel);
            formattedLines.push(indent + '• ' + content);
            return;
        }

        formattedLines.push(line);
    });

    let formattedText = formattedLines.join('\n');
    formattedText = formattedText.replace(/\n{3,}/g, '\n\n');
    return formattedText;
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded - Initializing script...');

    // Get all form elements (keeping existing declarations)
    const queryForm = document.getElementById('query-form');
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

    // Enhanced query history handling
    function updateQueryHistory(history) {
        while (queryHistoryDropdown.options.length > 1) {
            queryHistoryDropdown.remove(1);
        }

        if (history && history.length > 0) {
            history.forEach(entry => {
                const option = document.createElement('option');
                option.value = entry.query;
                option.textContent = entry.query;
                queryHistoryDropdown.appendChild(option);
            });
        }
    }

    // Clear form function
    function clearForm() {
        queryInput.value = '';
        confidenceInput.value = '';
        relevanceInput.value = '';
        if (enableDateRange.checked) {
            document.getElementById('start-date').value = '';
            document.getElementById('end-date').value = '';
            enableDateRange.checked = false;
            dateRangeInputs.style.display = 'none';
        }
    }

    // Clear results function
    function clearResults() {
        llmResponse.style.display = 'none';
        docsTable.style.display = 'none';
        resultsContainer.innerHTML = "";
        llmContent.innerHTML = "";
    }

    // Keep existing event listeners
    enableDateRange.addEventListener('change', () => {
        dateRangeInputs.style.display = enableDateRange.checked ? 'block' : 'none';
    });

    // Enhanced query history dropdown handler
    queryHistoryDropdown.addEventListener('change', () => {
        const selectedQuery = queryHistoryDropdown.value;
        if (selectedQuery) {
            queryInput.value = selectedQuery;
            queryInput.style.height = 'auto';
            queryInput.style.height = queryInput.scrollHeight + 'px';
            // Optional: Auto-submit when selecting from history
            // queryForm.dispatchEvent(new Event('submit'));
        }
    });

    // Enhanced form submit handler
    queryForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        console.log('Form submission started');

        // Clear old results immediately
        clearResults();

        // Show loading indicator
        loadingIndicator.style.display = 'flex';

        const queryValue = queryInput.value.trim();
        const confidenceValue = confidenceInput.value.trim();
        const relevanceValue = relevanceInput.value.trim();
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;

        const payload = { query: queryValue };
        if (confidenceValue) payload.confidence_threshold = confidenceValue;
        if (relevanceValue) payload.relevance_threshold = relevanceValue;
        if (enableDateRange.checked) {
            if (startDate) payload.start_date = startDate;
            if (endDate) payload.end_date = endDate;
        }

        try {
            const response = await fetch('/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            loadingIndicator.style.display = 'none';

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Query failed');
            }

            const data = await response.json();

            if (data.answer) {
                llmContent.innerHTML = cleanAndFormatText(data.answer);
                llmResponse.style.display = 'block';
            }

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
            }

            // Update query history and clear form after successful response
            if (data.search_history) {
                updateQueryHistory(data.search_history);
            }
            clearForm();

        } catch (error) {
            console.error('Error during query:', error);
            loadingIndicator.style.display = 'none';
            resultsContainer.innerHTML = `<p class="error">Error: ${error.message}</p>`;
        }
    });

    // Keep existing upload form handling
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
});