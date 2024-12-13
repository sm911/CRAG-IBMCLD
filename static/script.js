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

    // Keep your existing cleanAndFormatText function and other event handlers...
});