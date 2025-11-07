# 📊 Módulo de Relatórios & Indicadores

## 1. Objetivo do Módulo
Disponibilizar análises estratégicas e operacionais para apoiar decisões da equipe Sol Maior. O módulo compila dados acadêmicos, financeiros e de engajamento, com dashboards dinâmicos e exportação de relatórios.

---

## 2. Acesso e Permissões
| Perfil | Permissões |
|--------|------------|
| **Professor** | Visualizar indicadores da própria turma/alunos vinculados |
| **Secretaria** | Relatórios operacionais (matrículas, leads, agendas) |
| **Financeiro** | Relatórios financeiros e inadimplência |
| **Administrador** | Acesso completo a dashboards, exportações e configurações |

---

## 3. Tipos de Relatórios
- **Acadêmicos**: frequência, progresso, solicitações de reposição, avaliações.
- **Financeiros**: receitas por período, inadimplência, projeções de fluxo de caixa.
- **Marketing & Leads**: conversão de aulas experimentais, origem de lead, eficácia de campanhas.
- **Eventos**: participação em recitais, feedbacks de performances, logística.
- **Operacionais**: ocupação de salas, carga horária docente, uso de materiais.

---

## 4. Passo a Passo de Uso

### 4.1 Acessar dashboards
1. Abra **Relatórios > Dashboards**.
2. Selecione a visão desejada (Acadêmico, Financeiro, Marketing, Eventos).
3. Ajuste filtros (período, unidade, instrumento, professor).
4. Exporte dados em PDF/CSV usando os botões no canto superior direito.

![Placeholder](../static/screenshots/reports-dashboard.png)

### 4.2 Criar relatório customizado
1. Vá em **Relatórios > Personalizados**.
2. Escolha dataset base (alunos, faturas, aulas, eventos).
3. Defina colunas, filtros e agrupamentos.
4. Salve o relatório para acesso rápido futuro.
5. (Opcional) Agende envio periódico por email.

### 4.3 Configurar alertas
- Em **Relatórios > Alertas**, crie regras (ex.: inadimplência > 10%).
- Defina destinatários e frequência (diária, semanal, instantânea).
- Visualize histórico de alertas disparados.

---

## 5. Workflow Analítico
```
Coleta de dados → Tratamento → Dashboards e relatórios
                                ↘ Alertas automáticos → Ações corretivas
```

---

## 6. Erros Comuns e Soluções
| Questão | Possível causa | Solução |
|---------|----------------|---------|
| Dashboard vazio | Falta de dados no período filtrado | Ajustar filtros de data/unidade |
| Exportação falha | Arquivo grande demais | Refinar filtros ou exportar em lotes |
| Alerta não dispara | Regra mal configurada | Revisar condições e destinatários |

---

## 7. Integrações
- **BI Externo**: exporte via API ou conecte em endpoint dedicado (roadmap).
- **Financeiro & Acadêmico**: alimentam datasets automaticamente.
- **Comunicações**: dispara alertas por email/WhatsApp quando aplicável.

---

## 8. Checklist de Monitoramento
- [ ] Revisar dashboards críticos semanalmente.
- [ ] Ajustar metas/thresholds trimestralmente.
- [ ] Validar consistência entre relatórios e dados operacionais.
- [ ] Documentar insights relevantes para reuniões de diretoria.

---

## 9. Atualizações Futuras
- Implementar drill-down interativo em dashboards.
- Integrar com Power BI/Tableau para visualizações avançadas.
- Automatizar envio de resumos executivos semanais.

> Registre novas métricas e relatórios em [`updates.md`](../updates.md) para manter histórico das evoluções.
