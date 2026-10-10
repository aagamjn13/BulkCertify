const API_BASE_URL = 'http://localhost:8000';
let recipients = [];

// DOM Elements
const form = document.getElementById('add-recipient-form');
const nameInput = document.getElementById('name');
const emailInput = document.getElementById('email');
const recipientsList = document.getElementById('recipients-list');
const recipientCount = document.getElementById('recipient-count');
const generateBtn = document.getElementById('generate-btn');

const jobStatusSection = document.getElementById('job-status-section');
const jobStatusText = document.getElementById('job-status-text');
const jobSpinner = document.getElementById('job-spinner');
const certsContainer = document.getElementById('certificates-container');
const certsList = document.getElementById('certificates-list');

// Add Recipient
form.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const name = nameInput.value.trim();
    const email = emailInput.value.trim();
    
    if (name && email) {
        recipients.push({ name, email });
        nameInput.value = '';
        emailInput.value = '';
        nameInput.focus();
        
        renderRecipients();
    }
});

// Remove Recipient
function removeRecipient(index) {
    recipients.splice(index, 1);
    renderRecipients();
}

// Render Recipients List
function renderRecipients() {
    recipientCount.textContent = recipients.length;
    
    if (recipients.length === 0) {
        recipientsList.innerHTML = '<li class="empty-state">No recipients added yet.</li>';
        generateBtn.disabled = true;
        return;
    }
    
    generateBtn.disabled = false;
    recipientsList.innerHTML = '';
    
    recipients.forEach((rec, index) => {
        const li = document.createElement('li');
        li.innerHTML = `
            <div class="recipient-info">
                <span class="recipient-name">${rec.name}</span>
                <span class="recipient-email">${rec.email}</span>
            </div>
            <button type="button" class="btn btn-danger" onclick="removeRecipient(${index})" title="Remove">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"></path><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path></svg>
            </button>
        `;
        recipientsList.appendChild(li);
    });
}

// Generate Certificates
generateBtn.addEventListener('click', async () => {
    if (recipients.length === 0) return;
    
    generateBtn.disabled = true;
    generateBtn.innerHTML = `
        <div class="spinner" style="width: 18px; height: 18px; border-width: 2px;"></div>
        Starting Job...
    `;
    
    try {
        const response = await fetch(`${API_BASE_URL}/jobs/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ recipients }),
        });
        
        if (!response.ok) {
            let errMsg = 'Failed to create job';
            try {
                const errData = await response.json();
                if (errData.detail) {
                    if (Array.isArray(errData.detail)) {
                        errMsg = errData.detail.map(d => {
                            const field = d.loc[d.loc.length - 1];
                            return `${field}: ${d.msg}`;
                        }).join(' | ');
                    } else if (typeof errData.detail === 'string') {
                        errMsg = errData.detail;
                    }
                }
            } catch (e) {}
            throw new Error(errMsg);
        }
        
        const job = await response.json();
        startPolling(job.id);
        
        // UI updates
        jobStatusSection.classList.remove('hidden');
        jobStatusSection.scrollIntoView({ behavior: 'smooth' });
        
    } catch (error) {
        alert('Error starting job: ' + error.message);
        resetGenerateButton();
    }
});

function resetGenerateButton() {
    generateBtn.disabled = false;
    generateBtn.innerHTML = `
        Generate Certificates
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>
    `;
}

// Poll Job Status
async function startPolling(jobId) {
    jobStatusText.textContent = 'Processing...';
    jobSpinner.style.display = 'block';
    certsContainer.classList.add('hidden');
    
    const interval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`);
            if (!response.ok) throw new Error('Failed to fetch job status');
            
            const job = await response.json();
            
            if (job.status === 'completed' || job.status === 'failed') {
                clearInterval(interval);
                handleJobCompletion(job);
            }
        } catch (error) {
            console.error('Polling error:', error);
            // Optionally, stop polling after multiple failures
        }
    }, 1500);
}

// Handle Completion
function handleJobCompletion(job) {
    resetGenerateButton();
    jobSpinner.style.display = 'none';
    
    if (job.status === 'failed') {
        jobStatusText.textContent = 'Job Failed';
        jobStatusText.style.color = 'var(--danger-color)';
        return;
    }
    
    jobStatusText.textContent = 'Certificates Generated Successfully!';
    jobStatusText.style.color = 'var(--success-color)';
    
    certsContainer.classList.remove('hidden');
    renderCertificates(job.certificates);
    
    // Clear the recipient input list now that the job is complete
    recipients = [];
    renderRecipients();
}

// Render Certificates
function renderCertificates(certificates) {
    certsList.innerHTML = '';
    
    if (!certificates || certificates.length === 0) {
        certsList.innerHTML = '<li class="empty-state">No certificates generated.</li>';
        return;
    }
    
    certificates.forEach(cert => {
        const li = document.createElement('li');
        
        let statusBadge = '';
        let actionButton = '';
        
        if (cert.status === 'generated') {
            statusBadge = '<span class="badge generated">Generated</span>';
            actionButton = `
                <a href="${API_BASE_URL}/certificates/${cert.id}/download" class="btn btn-download" download>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                    Download
                </a>
            `;
        } else if (cert.status === 'failed') {
            statusBadge = '<span class="badge failed">Failed</span>';
        } else {
            statusBadge = '<span class="badge pending">Pending</span>';
        }
        
        li.innerHTML = `
            <div class="cert-info">
                <span class="cert-name">${cert.recipient_name}</span>
                <span class="recipient-email">${cert.recipient_email}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 1rem;">
                ${statusBadge}
                ${actionButton}
            </div>
        `;
        
        certsList.appendChild(li);
    });
}
