async function sendQuery() {
    const question = document.getElementById('question').value;
    const source = document.getElementById('source').value;
    const llm_choice = document.getElementById('llm_choice').value;
    const response = await fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, source, llm_choice })
    });
    const result = await response.json();
    alert(result.result); // Replace with better UI feedback
}