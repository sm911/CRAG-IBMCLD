document.getElementById('query-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const query = document.getElementById('query').value;
    const confidenceThreshold = document.getElementById('confidence-threshold').value || 0;
    const relevanceThreshold = document.getElementById('relevance-threshold').value || 0;
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;

    const loadingIndicator = document.getElementById('loading-indicator');
    loadingIndicator.style.display = 'block';

    try {
        const response = await fetch('/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query,
                confidence_threshold: confidenceThreshold,
                relevance_threshold: relevanceThreshold,
                start_date: startDate,
                end_date: endDate
            })
        });

        const data = await response.json();
        loadingIndicator.style.display = 'none';

        // Display LLM response
        const llmResponse = document.getElementById('llm-response');
        const llmContent = document.getElementById('llm-content');
        if (data.answer) {
            llmResponse.style.display = 'block';
            const p = document.createElement('p');
            p.textContent = data.answer;
            llmContent.innerHTML = '';
            llmContent.appendChild(p);
        } else {
            llmResponse.style.display = 'none';
        }

        // Display relevant documents
        const resultsContainer = document.getElementById('results-container');
        resultsContainer.innerHTML = '';

        if (data.relevant_documents && data.relevant_documents.length > 0) {
            data.relevant_documents.forEach(result => {
                const resultDiv = document.createElement('div');
                resultDiv.className = 'result';
                resultDiv.innerHTML = `
                    <h4>${result.title}</h4>
                    <div class="metadata">
                        <span><strong>Author:</strong> ${result.author}</span>
                        <span><strong>Confidence:</strong> ${result.confidence}</span>
                        <span><strong>Relevance:</strong> ${result.relevance}</span>
                        <span><strong>Document ID:</strong> ${result.document_id}</span>
                    </div>
                    <div class="passages">
                        <strong>Relevant Passages:</strong>
                        ${result.passages.map(passage => `
                            <div class="passage">${passage}</div>
                        `).join('')}
                    </div>
                `;
                resultsContainer.appendChild(resultDiv);
            });
        } else {
            resultsContainer.innerHTML = '<p>No matching documents found.</p>';
        }
    } catch (error) {
        loadingIndicator.style.display = 'none';
        console.error('Error:', error);
        document.getElementById('results-container').innerHTML = `
            <p class="error">Error: ${error.message}</p>
        `;
    }
});

document.getElementById('enable-date-range').addEventListener('change', function() {
    document.getElementById('date-range-inputs').style.display = this.checked ? 'block' : 'none';
});

document.getElementById('upload-form').addEventListener('submit', async function(event) {
    event.preventDefault();
    const fileInput = document.getElementById('file');
    const formData = new FormData();
    if (!fileInput.files[0]) {
        document.getElementById('upload-message').innerText = "Please select a file first.";
        return;
    }
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        document.getElementById('upload-message').innerText = data.message || data.error;
    } catch (error) {
        document.getElementById('upload-message').innerText = `An error occurred: ${error.message}`;
    }
});
