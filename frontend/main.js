// Certificate Dashboard Main Application
class CertificateDashboard {
    constructor() {
        this.apiBaseUrl = 'http://127.0.0.1:8000';
        this.certificates = [];
        this.isLoading = false;
        this.init();
    }

    init() {
        this.renderDashboard();
        this.checkApiHealth();
        this.bindEvents();
    }

    renderDashboard() {
        const app = document.getElementById('app');
        app.innerHTML = `
            <div class="dashboard">
                <header class="dashboard-header">
                    <h1>Certificate Approval Dashboard</h1>
                    <div class="api-status" id="apiStatus">
                        <span class="status-indicator checking"></span>
                        <span>Checking API...</span>
                    </div>
                </header>

                <main class="dashboard-main">
                    <div class="action-panel">
                        <button id="extractBtn" class="btn btn-primary">
                            <span class="btn-icon">📊</span>
                            Extract Certificates
                        </button>
                    </div>

                    <div class="results-section" id="resultsSection" style="display: none;">
                        <div class="certificate-list" id="certificateList"></div>
                        <div class="approval-panel" id="approvalPanel" style="display: none;">
                            <div class="approval-card">
                                <h3>⚠️ Approval Required</h3>
                                <p>Do you approve pushing these certificates to calendar?</p>
                                <div class="approval-actions">
                                    <button id="approveBtn" class="btn btn-success">
                                        <span class="btn-icon">✅</span>
                                        Approve
                                    </button>
                                    <button id="rejectBtn" class="btn btn-danger">
                                        <span class="btn-icon">❌</span>
                                        Reject
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="response-section" id="responseSection" style="display: none;">
                        <div class="response-card">
                            <h3>API Response</h3>
                            <pre id="responseContent"></pre>
                        </div>
                    </div>
                </main>
            </div>

            <div class="toast" id="toast"></div>
            <div class="loading-overlay" id="loadingOverlay" style="display: none;">
                <div class="spinner"></div>
                <p>Processing...</p>
            </div>
        `;
    }

    bindEvents() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('#extractBtn')) {
                this.extractCertificates();
            }
            if (e.target.closest('#approveBtn')) {
                this.sendApproval('yes');
            }
            if (e.target.closest('#rejectBtn')) {
                this.sendApproval('no');
            }
            if (e.target.closest('.finalize-btn')) {
                const certNumber = e.target.dataset.cert;
                this.finalizeApproval(certNumber);
            }
        });
    }

    async checkApiHealth() {
        const statusElement = document.getElementById('apiStatus');
        try {
            const response = await fetch(`${this.apiBaseUrl}/`);
            let data = {};
            try {
                data = await response.json();
            } catch {
                data = {};
            }
            if (response.ok && data.status === 'API is running') {
                statusElement.innerHTML = `
                    <span class="status-indicator online"></span>
                    <span>API Connected</span>
                `;
            } else {
                throw new Error('API health check failed');
            }
        } catch (error) {
            statusElement.innerHTML = `
                <span class="status-indicator offline"></span>
                <span>API Offline</span>
            `;
            this.showToast('Failed to connect to API', 'error');
        }
    }

    async extractCertificates() {
        this.setLoading(true);
        try {
            const response = await fetch(`${this.apiBaseUrl}/extract_certificates`, {
                method: 'POST'
            });
            const data = await response.json();
            if (response.ok) {
                this.certificates = data.certificates || [];  // FIXED ✅
                this.handleExtractResponse(data);
                this.showToast('Certificates extracted successfully', 'success');
            } else {
                throw new Error(data.message || 'Failed to extract certificates');
            }
        } catch (error) {
            this.showToast(`Error: ${error.message}`, 'error');
        } finally {
            this.setLoading(false);
        }
    }

    handleExtractResponse(data) {
        const resultsSection = document.getElementById('resultsSection');
        const certificateList = document.getElementById('certificateList');
        const approvalPanel = document.getElementById('approvalPanel');
        const responseSection = document.getElementById('responseSection');
        const responseContent = document.getElementById('responseContent');

        resultsSection.style.display = 'block';

        if (this.certificates.length > 0) {
            this.renderCertificates(this.certificates);
        } else {
            certificateList.innerHTML = `
                <div class="info-card">
                    <h3>📋 Extraction Result</h3>
                    <p><strong>Status:</strong> ${data.status || 'Unknown'}</p>
                    <p><strong>Message:</strong> ${data.message || 'No details'}</p>
                </div>
            `;
        }

        if (data.status === 'Waiting for approval') {
            approvalPanel.style.display = 'block';
        }

        responseSection.style.display = 'block';
        responseContent.textContent = JSON.stringify(data, null, 2);
    }

    renderCertificates(certificates) {
        const certificateList = document.getElementById('certificateList');
        const certificateCards = certificates.map((cert, index) => `
            <div class="certificate-card">
                <div class="certificate-header">
                    <h4>Certificate #${index + 1}</h4>
                    <span class="status-badge pending">Pending</span>
                </div>
                <div class="certificate-details">
                    <p><strong>Number:</strong> ${cert.certificate_number || cert}</p>
                    <button class="btn btn-primary finalize-btn" data-cert="${cert.certificate_number || cert}">
                        Finalize Approval
                    </button>
                </div>
            </div>
        `).join('');

        certificateList.innerHTML = `
            <div class="certificates-header">
                <h3>📋 Extracted Certificates (${certificates.length})</h3>
            </div>
            <div class="certificates-grid">
                ${certificateCards}
            </div>
        `;
    }

    async sendApproval(decision) {
        this.setLoading(true);
        try {
            const response = await fetch(`${this.apiBaseUrl}/approval?user_input=${decision}`, {
                method: 'POST'
            });
            const data = await response.json();
            if (response.ok) {
                this.handleApprovalResponse(data, decision);
                this.showToast(
                    decision === 'yes' ? 'Certificates approved successfully' : 'Certificates rejected',
                    'success'
                );
            } else {
                throw new Error(data.message || 'Failed to send approval');
            }
        } catch (error) {
            this.showToast(`Error: ${error.message}`, 'error');
        } finally {
            this.setLoading(false);
        }
    }

    async finalizeApproval(certificateNumber) {
        this.setLoading(true);
        try {
            const response = await fetch(`${this.apiBaseUrl}/after_approval?certificate_number=${certificateNumber}`, {
                method: 'POST'
            });
            const data = await response.json();
            if (response.ok) {
                this.showToast(`Certificate ${certificateNumber} finalized`, 'success');
                this.updateCertificateStatus('approved');
            } else {
                throw new Error(data.message || 'Failed to finalize certificate');
            }
        } catch (error) {
            this.showToast(`Error: ${error.message}`, 'error');
        } finally {
            this.setLoading(false);
        }
    }

    handleApprovalResponse(data, decision) {
        const approvalPanel = document.getElementById('approvalPanel');
        const responseSection = document.getElementById('responseSection');
        const responseContent = document.getElementById('responseContent');

        approvalPanel.style.display = 'none';
        this.updateCertificateStatus(decision === 'yes' ? 'approved' : 'rejected');

        responseSection.style.display = 'block';
        responseContent.textContent = JSON.stringify(data, null, 2);
    }

    updateCertificateStatus(status) {
        const statusBadges = document.querySelectorAll('.status-badge');
        statusBadges.forEach(badge => {
            badge.className = `status-badge ${status}`;
            badge.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        });
    }

    setLoading(loading) {
        this.isLoading = loading;
        const loadingOverlay = document.getElementById('loadingOverlay');
        const extractBtn = document.getElementById('extractBtn');
        if (loading) {
            loadingOverlay.style.display = 'flex';
            if (extractBtn) extractBtn.disabled = true;
        } else {
            loadingOverlay.style.display = 'none';
            if (extractBtn) extractBtn.disabled = false;
        }
    }

    showToast(message, type = 'info') {
        const toast = document.getElementById('toast');
        toast.className = `toast ${type} show`;
        toast.textContent = message;
        setTimeout(() => {
            toast.className = 'toast';
        }, 4000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new CertificateDashboard();
});
