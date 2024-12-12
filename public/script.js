document.addEventListener('DOMContentLoaded', () => {
    // ... (keep existing variable declarations) ...

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

    // ... (keep rest of the existing code) ...
});