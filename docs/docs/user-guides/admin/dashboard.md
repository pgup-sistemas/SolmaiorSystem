# 📊 Dashboard Administrativo

!!! info "Centro de Controle do Sistema"

    O Dashboard Administrativo é o painel principal para administradores gerenciarem todas as operações da escola de música.

## 🎯 Visão Geral

O dashboard apresenta uma visão consolidada de todos os aspectos da escola:

- **Indicadores principais** em tempo real
- **Gráficos de performance** e tendências
- **Alertas e notificações** importantes
- **Acesso rápido** às funções administrativas

## 📈 Indicadores Principais

### Métricas Essenciais

| Indicador | Descrição | Atualização |
|-----------|-----------|-------------|
| 👥 **Total de Alunos** | Alunos ativos matriculados | Tempo real |
| 👨‍🏫 **Total de Professores** | Professores disponíveis | Tempo real |
| 🏢 **Salas Ativas** | Salas de aula configuradas | Tempo real |
| 🎵 **Aulas Hoje** | Aulas agendadas para hoje | A cada hora |
| 💰 **Receita Mensal** | Faturamento do mês atual | Diariamente |
| ⚠️ **Pagamentos Pendentes** | Cobranças em atraso | Tempo real |

### Status do Sistema

- **✅ Banco de dados**: Conectado e saudável
- **✅ Servidor web**: Operacional
- **✅ Emails**: Sistema funcionando
- **✅ Backups**: Último realizado em X horas

## 📊 Gráficos e Relatórios

### Receita Mensal

```chart
type: line
data:
  labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun']
  datasets:
    - label: Receita (R$)
      data: [12500, 13200, 11800, 14100, 13800, 15200]
      borderColor: '#4CAF50'
      backgroundColor: 'rgba(76, 175, 80, 0.1)'
```

### Alunos por Instrumento

```chart
type: doughnut
data:
  labels: ['Piano', 'Violino', 'Canto', 'Violão', 'Teoria']
  datasets:
    - data: [45, 32, 28, 22, 18]
      backgroundColor:
        - '#FF6384'
        - '#36A2EB'
        - '#FFCE56'
        - '#4BC0C0'
        - '#9966FF'
```

### Frequência de Aulas

```chart
type: bar
data:
  labels: ['Semana 1', 'Semana 2', 'Semana 3', 'Semana 4']
  datasets:
    - label: Aulas Realizadas
      data: [156, 148, 162, 159]
      backgroundColor: '#2196F3'
    - label: Faltas
      data: [12, 8, 15, 6]
      backgroundColor: '#F44336'
```

## 🚨 Alertas e Notificações

### Alertas Críticos

!!! danger "Ação Imediata Necessária"

    - **3 pagamentos** vencidos há mais de 30 dias
    - **2 professores** sem disponibilidade cadastrada
    - **Backup falhou** na última execução

### Avisos Importantes

!!! warning "Atenção Necessária"

    - **5 alunos** com risco de evasão detectado
    - **Sala 03** necessita manutenção
    - **2 aulas** sem professor definido

### Informações Gerais

!!! info "Atualizações do Sistema"

    - Nova versão 2.1 disponível para atualização
    - Relatório mensal gerado automaticamente
    - 3 novos alunos cadastrados hoje

## 🏗️ Ações Rápidas

### Gestão de Usuários

- [**👤 Criar Novo Usuário**](users.md) - Adicionar professores, alunos ou staff
- [**🔍 Buscar Usuários**](users.md) - Localizar e editar perfis
- [**📋 Relatório de Usuários**](reports.md) - Exportar dados completos

### Configurações do Sistema

- [**⚙️ Configurações Gerais**](settings.md) - Parâmetros globais
- [**💰 Planos de Pagamento**](settings.md) - Configurar mensalidades
- [**📧 Templates de Email**](settings.md) - Personalizar comunicações

### Operações Diárias

- [**📅 Agenda Global**](global-schedule.md) - Visualizar todas as aulas
- [**🎭 Gerenciar Recitais**](recitals.md) - Organizar eventos
- [**📊 Relatórios**](reports.md) - Análises detalhadas

## 📱 Acesso Móvel

O dashboard é totalmente responsivo e otimizado para:

- **📱 Smartphones**: Interface adaptada para telas pequenas
- **📲 Tablets**: Layout otimizado para tablets
- **💻 Desktops**: Experiência completa em monitores grandes

### Funcionalidades Mobile

- **Toque rápido** para ações principais
- **Swipe gestures** para navegação
- **Notificações push** para alertas críticos
- **Modo offline** para visualização básica

## 🔍 Filtros e Pesquisa

### Filtros por Período

```yaml
- Hoje
- Esta Semana
- Este Mês
- Últimos 3 Meses
- Personalizado
```

### Filtros por Categoria

```yaml
- Alunos
- Professores
- Financeiro
- Acadêmico
- Sistema
```

### Busca Avançada

- **Por nome**: Buscar usuários específicos
- **Por instrumento**: Filtrar por área musical
- **Por status**: Ativos, inativos, pendentes
- **Por data**: Intervalos personalizados

## 📋 Relatórios Rápidos

### Relatórios Disponíveis

| Relatório | Frequência | Destinatários |
|-----------|------------|---------------|
| **Financeiro Diário** | Diariamente | Administração |
| **Ocupação de Salas** | Semanalmente | Coordenação |
| **Performance Professores** | Mensalmente | Direção |
| **Evasão de Alunos** | Trimestralmente | Conselho |

### Geração Automática

```python
# Exemplo de configuração de relatório automático
AUTOMATIC_REPORTS = {
    'daily_financial': {
        'schedule': '08:00',
        'recipients': ['admin@escola.com', 'financeiro@escola.com'],
        'format': 'PDF',
        'include_charts': True
    },
    'weekly_occupancy': {
        'schedule': 'monday 09:00',
        'recipients': ['coordenacao@escola.com'],
        'format': 'Excel',
        'include_details': True
    }
}
```

## 🔐 Segurança e Auditoria

### Logs de Acesso

- **Últimos logins** por usuário
- **Ações administrativas** realizadas
- **Tentativas de acesso** suspeitas
- **Alterações críticas** no sistema

### Backup Status

- **✅ Último backup**: 2 horas atrás
- **📊 Tamanho**: 1.2 GB
- **⏱️ Duração**: 15 minutos
- **📍 Localização**: AWS S3 + Local

## 🎯 Próximos Passos

### Otimizações Sugeridas

1. **Configurar alertas automáticos** para pagamentos em atraso
2. **Implementar backup automático** diário
3. **Revisar permissões** de usuários administrativos
4. **Atualizar versão** do sistema quando disponível

### Expansão Planejada

- **Nova filial** em planejamento para Q2
- **Integração WhatsApp** para notificações
- **Aplicativo mobile** para professores
- **Sistema de videoconferência** integrado

---

!!! tip "Dicas de Uso"

    - **Acesse diariamente** para acompanhar operações
    - **Configure notificações** para alertas importantes
    - **Use filtros** para análises específicas
    - **Exporte relatórios** regularmente para registros

!!! info "Atualização Automática"

    O dashboard é atualizado automaticamente a cada 5 minutos com os dados mais recentes do sistema.