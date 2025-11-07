// ============================================================================
// COMPONENTES REUTILIZÁVEIS - UI/UX PROFISSIONAL
// ============================================================================

/**
 * Sistema de Notificações Toast
 */
class Toast {
    static show(message, type = 'info', duration = 3000) {
        const toastContainer = document.getElementById('toast-container') || this.createContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type} animate-fade-in`;
        toast.innerHTML = `
            <div class="flex items-center gap-3">
                <span class="toast-icon">${this.getIcon(type)}</span>
                <span class="toast-message">${message}</span>
                <button class="toast-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        if (duration > 0) {
            setTimeout(() => toast.remove(), duration);
        }
        
        return toast;
    }
    
    static createContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'fixed top-4 right-4 z-50 space-y-2';
        document.body.appendChild(container);
        return container;
    }
    
    static getIcon(type) {
        const icons = {
            'success': '✓',
            'error': '✕',
            'warning': '⚠',
            'info': 'ℹ'
        };
        return icons[type] || icons['info'];
    }
    
    static success(message) { return this.show(message, 'success'); }
    static error(message) { return this.show(message, 'error'); }
    static warning(message) { return this.show(message, 'warning'); }
    static info(message) { return this.show(message, 'info'); }
}

/**
 * Modal Dialogs
 */
class Modal {
    static open(title, content, options = {}) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay animate-fade-in';
        modal.innerHTML = `
            <div class="modal-content animate-slide-up">
                <div class="modal-header">
                    <h2 class="modal-title">${title}</h2>
                    <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">×</button>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
                <div class="modal-footer">
                    ${options.buttons ? options.buttons : `
                        <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancelar</button>
                        <button class="btn btn-primary" onclick="this.closest('.modal-overlay').remove()">Confirmar</button>
                    `}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });
        
        return modal;
    }
    
    static confirm(message, onConfirm, onCancel) {
        const buttons = `
            <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove(); ${onCancel || ''}">Cancelar</button>
            <button class="btn btn-primary" onclick="this.closest('.modal-overlay').remove(); ${onConfirm}">Confirmar</button>
        `;
        return this.open('Confirmação', message, { buttons });
    }
}

/**
 * Loading Spinner
 */
class Spinner {
    static show(message = 'Carregando...') {
        const spinner = document.createElement('div');
        spinner.id = 'global-spinner';
        spinner.className = 'spinner-overlay';
        spinner.innerHTML = `
            <div class="spinner-content">
                <div class="spinner-circle"></div>
                <p class="spinner-text">${message}</p>
            </div>
        `;
        document.body.appendChild(spinner);
        return spinner;
    }
    
    static hide() {
        const spinner = document.getElementById('global-spinner');
        if (spinner) spinner.remove();
    }
}

/**
 * Validação de Formulários
 */
class FormValidator {
    static validate(formElement) {
        const errors = [];
        const inputs = formElement.querySelectorAll('[required]');
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                errors.push(`${input.getAttribute('data-label') || input.name} é obrigatório`);
                input.classList.add('input-error');
            } else {
                input.classList.remove('input-error');
            }
        });
        
        return errors;
    }
    
    static showErrors(errors) {
        errors.forEach(error => Toast.error(error));
    }
}

/**
 * Data Table com Paginação
 */
class DataTable {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            pageSize: 10,
            sortable: true,
            searchable: true,
            ...options
        };
        this.currentPage = 1;
        this.data = [];
    }
    
    render(data, columns) {
        this.data = data;
        const start = (this.currentPage - 1) * this.options.pageSize;
        const end = start + this.options.pageSize;
        const pageData = data.slice(start, end);
        
        let html = '<div class="data-table-wrapper">';
        html += '<table class="data-table">';
        
        // Header
        html += '<thead><tr>';
        columns.forEach(col => {
            html += `<th>${col.label}</th>`;
        });
        html += '</tr></thead>';
        
        // Body
        html += '<tbody>';
        pageData.forEach(row => {
            html += '<tr>';
            columns.forEach(col => {
                html += `<td>${row[col.key] || '-'}</td>`;
            });
            html += '</tr>';
        });
        html += '</tbody></table>';
        
        // Pagination
        const totalPages = Math.ceil(data.length / this.options.pageSize);
        html += `<div class="pagination">
            <button onclick="this.table.previousPage()" ${this.currentPage === 1 ? 'disabled' : ''}>← Anterior</button>
            <span>Página ${this.currentPage} de ${totalPages}</span>
            <button onclick="this.table.nextPage()" ${this.currentPage === totalPages ? 'disabled' : ''}>Próxima →</button>
        </div></div>`;
        
        this.container.innerHTML = html;
    }
    
    nextPage() {
        this.currentPage++;
        this.render(this.data);
    }
    
    previousPage() {
        if (this.currentPage > 1) this.currentPage--;
        this.render(this.data);
    }
}

/**
 * Dropdown Menu
 */
class Dropdown {
    static init() {
        document.querySelectorAll('.dropdown-trigger').forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.stopPropagation();
                const menu = trigger.nextElementSibling;
                menu.classList.toggle('hidden');
            });
        });
        
        document.addEventListener('click', () => {
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.classList.add('hidden');
            });
        });
    }
}

/**
 * Tabs
 */
class Tabs {
    static init() {
        document.querySelectorAll('.tabs-container').forEach(container => {
            const triggers = container.querySelectorAll('.tab-trigger');
            const contents = container.querySelectorAll('.tab-content');
            
            triggers.forEach((trigger, index) => {
                trigger.addEventListener('click', () => {
                    triggers.forEach(t => t.classList.remove('active'));
                    contents.forEach(c => c.classList.add('hidden'));
                    
                    trigger.classList.add('active');
                    contents[index].classList.remove('hidden');
                });
            });
        });
    }
}

/**
 * Accordion
 */
class Accordion {
    static init() {
        document.querySelectorAll('.accordion-item').forEach(item => {
            const header = item.querySelector('.accordion-header');
            const content = item.querySelector('.accordion-content');
            
            header.addEventListener('click', () => {
                const isOpen = content.classList.contains('hidden');
                
                document.querySelectorAll('.accordion-content').forEach(c => {
                    c.classList.add('hidden');
                });
                
                if (isOpen) {
                    content.classList.remove('hidden');
                }
            });
        });
    }
}

/**
 * Busca em Tempo Real
 */
class Search {
    static init(inputSelector, resultsSelector, searchFunction) {
        const input = document.querySelector(inputSelector);
        const results = document.querySelector(resultsSelector);
        
        input.addEventListener('input', async (e) => {
            const query = e.target.value;
            if (query.length < 2) {
                results.innerHTML = '';
                return;
            }
            
            const data = await searchFunction(query);
            results.innerHTML = data.map(item => `
                <div class="search-result" onclick="this.select('${item.id}')">
                    ${item.name}
                </div>
            `).join('');
        });
    }
}

/**
 * Gráficos Simples
 */
class Chart {
    static bar(containerId, data, options = {}) {
        const container = document.getElementById(containerId);
        const max = Math.max(...data.map(d => d.value));
        
        let html = '<div class="chart-bar">';
        data.forEach(item => {
            const percentage = (item.value / max) * 100;
            html += `
                <div class="bar-item">
                    <div class="bar-label">${item.label}</div>
                    <div class="bar-container">
                        <div class="bar-fill" style="width: ${percentage}%"></div>
                    </div>
                    <div class="bar-value">${item.value}</div>
                </div>
            `;
        });
        html += '</div>';
        
        container.innerHTML = html;
    }
    
    static pie(containerId, data) {
        const container = document.getElementById(containerId);
        const total = data.reduce((sum, item) => sum + item.value, 0);
        
        let html = '<div class="chart-pie">';
        let angle = 0;
        
        data.forEach(item => {
            const percentage = (item.value / total) * 360;
            html += `
                <div class="pie-item" style="--angle: ${angle}deg; --percentage: ${percentage}deg;">
                    <span class="pie-label">${item.label}: ${item.value}</span>
                </div>
            `;
            angle += percentage;
        });
        html += '</div>';
        
        container.innerHTML = html;
    }
}

/**
 * Inicialização Global
 */
document.addEventListener('DOMContentLoaded', () => {
    Dropdown.init();
    Tabs.init();
    Accordion.init();
});

// Exportar para uso global
window.Toast = Toast;
window.Modal = Modal;
window.Spinner = Spinner;
window.FormValidator = FormValidator;
window.DataTable = DataTable;
window.Chart = Chart;
