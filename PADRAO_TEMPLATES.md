# 📋 PADRÃO DE TEMPLATES - SOLMAIOR v2.1

**Data:** Outubro 2025 | **Status:** ✅ Consolidado | **Versão:** 2.1

---

## ✅ Refatoração Realizada

### Antes (❌ Ineficiente)
```
/app/templates/
├── base.html                  (Original)
├── base_professional.html     (Duplicado)
├── base_simple.html           (Duplicado)
└── (Outras templates)
```

**Problemas:**
- ⚠️ 3 templates base diferentes
- ⚠️ Confusão sobre qual usar
- ⚠️ Manutenção difícil
- ⚠️ Inconsistência visual
- ⚠️ Código duplicado

### Depois (✅ Profissional)
```
/app/templates/
├── base.html                  (Único padrão profissional)
├── auth/
│   ├── login.html
│   ├── register.html
│   └── forgot_password.html
├── admin/
│   ├── dashboard.html
│   ├── users.html
│   └── (outras)
├── student/
├── teacher/
├── secretary/
├── financial/
├── documents/
├── profile/
└── public/
```

**Benefícios:**
- ✅ Um único padrão
- ✅ Consistência visual
- ✅ Fácil manutenção
- ✅ Sem duplicação
- ✅ Profissional

---

## 📐 Estrutura do Template Base

### base.html - Padrão Único

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <!-- Meta tags -->
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- CSS - Carregado UMA VEZ -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="https://cdn.tailwindcss.com">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/professional.css') }}">
    
    <!-- Scripts -->
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    
    {% block extra_css %}{% endblock %}
</head>
<body class="bg-gray-50">
    <!-- Header/Navbar -->
    <nav>...</nav>
    
    <!-- Sidebar (se necessário) -->
    {% if current_user.is_authenticated %}
        <aside>...</aside>
    {% endif %}
    
    <!-- Main Content -->
    <main>
        <!-- Flash Messages -->
        {% with messages = get_flashed_messages(with_categories=true) %}...{% endwith %}
        
        <!-- Breadcrumb -->
        {% block breadcrumb %}{% endblock %}
        
        <!-- Page Title -->
        {% block page_title %}{% endblock %}
        
        <!-- Page Content -->
        {% block content %}{% endblock %}
    </main>
    
    <!-- Footer -->
    <footer>...</footer>
    
    <!-- Scripts -->
    <script src="{{ url_for('static', filename='js/components.js') }}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

---

## 🎯 Como Usar

### 1. Template Simples (Herança)

```html
<!-- page.html -->
{% extends "base.html" %}

{% block title %}Minha Página{% endblock %}

{% block content %}
    <div class="card">
        <h1>Bem-vindo!</h1>
        <p>Conteúdo aqui...</p>
    </div>
{% endblock %}
```

### 2. Com Breadcrumb

```html
{% extends "base.html" %}

{% block breadcrumb %}
    <nav class="breadcrumb">
        <a href="{{ url_for('admin.dashboard') }}">Admin</a>
        <span>/</span>
        <span>Usuários</span>
    </nav>
{% endblock %}

{% block page_title %}
    <h1>Gerenciar Usuários</h1>
{% endblock %}

{% block content %}
    <!-- Conteúdo -->
{% endblock %}
```

### 3. Com CSS Extra

```html
{% extends "base.html" %}

{% block extra_css %}
    <style>
        .custom-class {
            /* Estilos específicos da página */
        }
    </style>
{% endblock %}

{% block content %}
    <!-- Conteúdo -->
{% endblock %}
```

### 4. Com JavaScript Extra

```html
{% extends "base.html" %}

{% block extra_js %}
    <script>
        // JavaScript específico da página
        document.addEventListener('DOMContentLoaded', () => {
            // Inicializar componentes
        });
    </script>
{% endblock %}

{% block content %}
    <!-- Conteúdo -->
{% endblock %}
```

---

## 📁 Estrutura de Diretórios

```
/app/templates/
│
├── base.html                    ← ÚNICO PADRÃO
│
├── auth/
│   ├── login.html               (Standalone - sem extends)
│   ├── register.html
│   └── forgot_password.html
│
├── admin/
│   ├── dashboard.html           (extends base.html)
│   ├── users.html
│   ├── schedule.html
│   ├── rooms.html
│   ├── financial.html
│   └── recitals.html
│
├── student/
│   ├── dashboard.html
│   ├── schedule.html
│   ├── materials.html
│   └── recitals.html
│
├── teacher/
│   ├── dashboard.html
│   ├── availability.html
│   ├── schedule.html
│   └── students.html
│
├── secretary/
│   ├── dashboard.html
│   └── (outras)
│
├── financial/
│   ├── dashboard.html
│   └── (outras)
│
├── documents/
│   └── (templates de documentos)
│
├── profile/
│   ├── index.html
│   └── settings.html
│
└── public/
    ├── index.html
    ├── about.html
    ├── news.html
    └── trial_lesson.html
```

---

## 🎨 Componentes Disponíveis

### Cards
```html
<div class="card">
    <h3>Título</h3>
    <p>Conteúdo</p>
</div>
```

### Botões
```html
<button class="btn btn-primary">Primário</button>
<button class="btn btn-secondary">Secundário</button>
```

### Formulários
```html
<form>
    <div class="form-group">
        <label>Campo</label>
        <input type="text" class="form-input">
    </div>
</form>
```

### Tabelas
```html
<table class="data-table">
    <thead>
        <tr>
            <th>Coluna 1</th>
            <th>Coluna 2</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Dados</td>
            <td>Dados</td>
        </tr>
    </tbody>
</table>
```

---

## ✅ Checklist de Boas Práticas

- [x] Um único template base
- [x] CSS carregado uma única vez
- [x] Herança de templates
- [x] Blocos bem definidos
- [x] Componentes reutilizáveis
- [x] Sem duplicação
- [x] Profissional e consistente
- [ ] Documentação completa
- [ ] Testes de responsividade
- [ ] Otimização de performance

---

## 🚀 Padrão de Nomenclatura

### Templates Autenticadas
```
/admin/dashboard.html          → {% extends "base.html" %}
/student/schedule.html         → {% extends "base.html" %}
/teacher/availability.html     → {% extends "base.html" %}
```

### Templates Públicas
```
/auth/login.html               → Standalone (sem extends)
/auth/register.html            → Standalone (sem extends)
/public/index.html             → {% extends "base.html" %}
```

### Padrão de Nomes
```
✅ CORRETO
- dashboard.html
- user_list.html
- schedule_edit.html
- financial_report.html

❌ ERRADO
- admin_dashboard.html
- list_users.html
- edit_schedule.html
- report_financial.html
```

---

## 📊 Comparação

| Aspecto | Antes | Depois |
|---------|-------|--------|
| Templates Base | 3 | 1 |
| Duplicação | Alta | Nenhuma |
| Manutenção | Difícil | Fácil |
| Consistência | Baixa | Alta |
| Performance | Lenta | Rápida |
| Profissionalismo | Médio | Alto |

---

## 💡 Dicas

### 1. Sempre use herança
```html
{% extends "base.html" %}
```

### 2. Use blocos bem definidos
```html
{% block title %}...{% endblock %}
{% block breadcrumb %}...{% endblock %}
{% block page_title %}...{% endblock %}
{% block content %}...{% endblock %}
{% block extra_css %}...{% endblock %}
{% block extra_js %}...{% endblock %}
```

### 3. Reutilize componentes
```html
<div class="card">
    <div class="card-header">Título</div>
    <div class="card-body">Conteúdo</div>
    <div class="card-footer">Rodapé</div>
</div>
```

### 4. Use classes Tailwind
```html
<div class="flex justify-between items-center p-4 bg-white rounded-lg shadow-md">
    <!-- Conteúdo -->
</div>
```

---

## 🎯 Conclusão

✅ **Um único template base profissional**
✅ **Sem duplicação ou confusão**
✅ **Fácil de manter e escalar**
✅ **Consistência visual garantida**
✅ **Performance otimizada**

---

**Versão:** 2.1 | **Status:** ✅ Consolidado
**Data:** Outubro 2025 | **Responsável:** Arquiteto Senior
