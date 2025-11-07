# 💰 Módulo Financeiro

## 1. Objetivo do Módulo
Controlar receitas, cobranças, inadimplência e auditoria financeira da Escola Sol Maior. O módulo integra processos de faturamento, pagamentos, descontos e relatórios.

---

## 2. Acesso e Permissões
| Perfil | Permissões |
|--------|------------|
| **Aluno/Responsável** | Visualizar faturas, efetuar pagamentos, baixar recibos |
| **Secretaria** | Emitir faturas, registrar recebimentos, aplicar descontos (quando autorizado) |
| **Financeiro** | Acesso completo, conciliações bancárias, renegociações |
| **Administrador** | Visão global, auditoria, configuração de planos e políticas |

---

## 3. Componentes do Módulo
- **Planos e Tabelas de Preço**: cadastro de produtos/serviços e valores.
- **Faturamento**: geração automática de mensalidades e cobranças avulsas.
- **Recebimentos**: registro de pagamentos (cartão, PIX, boleto, presencial).
- **Inadimplência**: acompanhamento de atrasos, envio de notificações, renegociação.
- **Auditoria Financeira**: logs detalhados de alterações sensíveis.
- **Relatórios**: DRE simplificado, fluxo de caixa, receitas por instrumento.

---

## 4. Passo a Passo de Uso

### 4.1 Configurar planos
1. Acesse **Financeiro > Planos**.
2. Clique em **Novo plano** para definir instrumentação, duração, valor e política de desconto.
3. Associe o plano às turmas ou matrículas específicas.

### 4.2 Gerar faturas
1. Em **Financeiro > Faturamento**, selecione o período.
2. Clique em **Gerar faturas** (automático para todos os alunos ativos).
3. Revise valores e condições especiais antes de publicar.
4. Publicadas, as faturas ficam visíveis no portal do aluno/resp.

![Placeholder](../static/screenshots/finance-invoice.png)

### 4.3 Registrar pagamentos
1. Vá em **Financeiro > Recebimentos**.
2. Selecione a fatura.
3. Informe método de pagamento e data da baixa.
4. Anexe comprovante digital (opcional).

### 4.4 Automatizar cobranças
- Integração com gateway: configure em **Configurações > Pagamentos**.
- Defina lembretes automáticos: 5 dias antes do vencimento, no dia, 3 dias após o vencimento.
- Para PIX, o sistema gera QR Codes únicos.

### 4.5 Auditoria
1. Abra **Financeiro > Auditoria**.
2. Analise logs: criação/alteração de faturas, descontos aplicados, exclusões.
3. Aprove ou rejeite alterações com justificativa.

---

## 5. Workflow Financeiro Simplificado
```
Plano definido → Matrícula → Geração automática de faturas
               → Envio de lembrete → Recebimento → Baixa automática/manual
               → Auditoria em caso de ajustes ou descontos especiais
```

---

## 6. Erros Comuns e Soluções
| Situação | Possível causa | Solução |
|----------|----------------|---------|
| Fatura duplicada | Matrícula registrada duas vezes | Verifique histórico da matrícula e exclua duplicidade |
| Pagamento não reconhecido | Falha na conciliação com gateway | Execute conciliação manual e anexe comprovante |
| Desconto não aplicado | Falta de permissão do usuário | Solicite autorização ou ajuste as permissões |

---

## 7. Relatórios Disponíveis
- **Resumo Mensal de Receitas**.
- **Inadimplência por faixa de atraso**.
- **Receitas por instrumento/professor**.
- **Comparativo anual**.

---

## 8. Integrações
- **Acadêmico**: vínculo de planos com matrículas.
- **Agenda**: bloqueios para inadimplentes (opcional).
- **Dashboard de Administradores**: métricas financeiras atualizadas.

---

## 9. Checklist de Fechamento Mensal
- [ ] Conferir todas as faturas do mês.
- [ ] Checar conciliação bancária.
- [ ] Emitir DRE simplificado.
- [ ] Registrar ajustes e aprovações em Auditoria.
- [ ] Atualizar indicadores do dashboard executivo.

---

## 10. Atualizações Futuras
- Integração com ERP contábil.
- Automação de notas fiscais eletrônicas.
- Recursos de cobrança judicial.

> Documente evoluções no arquivo [`updates.md`](../updates.md).
