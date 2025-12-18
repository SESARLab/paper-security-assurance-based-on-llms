lucide.createIcons();

const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('main-content');
const toggleButton = document.getElementById('toggle-sidebar');
const loadingIndicator = document.getElementById('loading');

toggleButton.addEventListener('click', () => {
    sidebar.classList.toggle('-translate-x-full');
    mainContent.classList.toggle('ml-0');
    mainContent.classList.toggle('ml-64');
});

document.getElementById('promptForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const prompt = document.getElementById('promptInput').value;
    loadingIndicator.classList.remove('hidden');

    try {
        const response = await fetch('http://127.0.0.1:8080/prompt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt }),
        });
        const data = await response.json();
        updateAccordions(data);
    } catch (error) {
        console.error('Error:', error);
    } finally {
        loadingIndicator.classList.add('hidden');
    }
});

function updateAccordions(results) {
    const container = document.getElementById('accordionContainer');
    container.innerHTML = '';

    results.probes.forEach((probe, index) => {
        const accordion = document.createElement('div');
        accordion.className = 'border border-gray-200 rounded-lg';
        accordion.innerHTML = `
                    <button class="w-full p-4 text-left font-medium text-white bg-gray-700 hover:bg-gray-600 focus:outline-none" onclick="toggleAccordion(${index})">
                        ${probe.name}
                        <i data-lucide="chevron-down" class="float-right w-5 h-5"></i>
                    </button>
                    <div id="accordion-content-${index}" class="hidden p-4 border-t border-gray-200">
                        <pre>${probe.config}</pre>
                    </div>
                `;
        container.appendChild(accordion);
    });
    Prism.highlightAll();
    lucide.createIcons();
}
// Function to toggle accordion
function toggleAccordion(index) {
    const content = document.getElementById(`accordion-content-${index}`);
    content.classList.toggle('hidden');
}