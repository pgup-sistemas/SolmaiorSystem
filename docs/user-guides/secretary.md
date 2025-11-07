# 🗂 Manual da Secretaria

## 1. Objetivo
A secretaria é responsável pelo relacionamento com alunos e responsáveis, pelo fluxo de matrícula, controle de documentos e comunicação institucional. Este manual descreve as rotinas do dia a dia dentro do sistema Sol Maior.

---

## 2. Acesso e Perfil
- Acesse `https://solmaior.com.br/app`.
- Use o login corporativo (perfil `secretary`).
- Caso tenha acesso a múltiplas unidades, selecione a unidade ao entrar.

> **Dica:** Crie um atalho no desktop para agilizar o acesso diário.

---

## 3. Painel da Secretaria
![Placeholder](../static/screenshots/secretary-dashboard.png)

### 3.1 Indicadores principais
- **Solicitações pendentes**: aulas experimentais, matrículas, transferências.
- **Documentos**: contratos aguardando assinatura digital.
- **Comunicações recentes**: mensagens de alunos e professores.
- **Alertas financeiros**: inadimplências críticas.

### 3.2 Menu lateral
| Seção | Descrição |
|-------|-----------|
| **Lead Management** | Funil de prospects e aulas experimentais |
| **Matrículas** | Processos em análise, aprovados e rejeitados |
| **Agenda** | Visão geral das aulas, salas e professores |
| **Financeiro** | Emissão de faturas, controle de pagamentos |
| **Documentos** | Geração e upload de contratos |
| **Comunicações** | Email marketing, avisos gerais |

---

## 4. Fluxo de Aulas Experimentais
1. Acesse **Lead Management > Trial Lessons**.
2. Veja os cards com status (Pendente, Agendado, Concluído, Cancelado).
3. Para cada solicitação:
   - Abrir detalhes.
   - Validar dados do interessado.
   - Agendar com professor e sala.
   - Enviar confirmação (o sistema dispara email com link).
4. Acompanhe confirmações dos alunos (indicadores verde/vermelho).

> **Erro comum:** Token de confirmação expira? Reenvie o email por **Reenviar Confirmação**.

---

## 5. Matrículas e Contratos
### 5.1 Aprovar matrícula
1. Acesse **Matrículas > Em análise**.
2. Verifique dados pessoais, instrumentos e planos.
3. Gere contrato em **Documentos > Gerar contrato**.
4. Envie para assinatura eletrônica.
5. Após assinatura, status muda para **Ativo** e o aluno passa a aparecer no módulo Acadêmico.

### 5.2 Renovação e trancamento
- Execute em **Matrículas > Gestão**.
- Trancamento temporário mantém cadastro mas suspende aulas.
- Renovação gera nova vigência e comunica financeiro.

---

## 6. Agenda e Recursos
- **Agenda** permite visualizar horários de professores e disponibilidade de salas.
- Use filtros por unidade, instrumento e professor.
- Ao criar evento, verifique conflitos de sala ou sobreposição de professor.

> **Atenção:** A agenda da secretaria tem poder de sobrescrever reservas com justificativa.

---

## 7. Comunicação com alunos e responsáveis
- Utilize **Comunicações > Mensagens** para e-mail/SMS segmentado.
- Crie templates padronizados (boas-vindas, lembrete de pagamento, convite para recital).
- Histórico fica armazenado por aluno (acessível na ficha individual).

---

## 8. Financeiro (visão da secretaria)
- Emitir faturas avulsas: **Financeiro > Faturamento Manual**.
- Aplicar descontos autorizados: **Financeiro > Descontos**.
- Registrar pagamentos presenciais no caixa: **Financeiro > Recebimentos**.

> **Erro comum:** Doppel pagamento no Pix. Marcar como "Conciliado manualmente" e anexar comprovante.

---

## 9. Relacionamento com Professores
- Receba pedidos de troca de horário via **Agenda > Solicitações**.
- Encaminhe recados especiais pelo chat interno (marcações @professor).
- Documente feedbacks relevantes em **Coordenação > Feedback dos Docentes**.

---

## 10. Relatórios
- **Relatório de capacidade**: mostra ocupação por sala/instrumento.
- **Relatório de conversão**: quantas aulas experimentais viraram matrículas.
- **Relatório financeiro resumido**: visão por mês e por status.

---

## 11. Perguntas Frequentes da Secretaria
| Pergunta | Resposta |
|----------|----------|
| **Como reabrir um lead perdido?** | Lead Management > Arquivados > Reabrir |
| **Contrato não envia para assinatura?** | Verifique configuração da integração (página Configurações > Assinaturas) |
| **Posso emitir declaração de matrícula?** | Sim, Documentos > Declarações |

Para mais respostas, consulte o [FAQ geral](../faq.md).

---

## 12. Suporte institucional
- **Canal:** secretaria@solmaior.com.br
- **Telefone:** (11) 98888-0000
- **Treinamento presencial:** mensal, consulte agenda interna.

> **Atualização constante:** registre melhorias e scripts úteis no arquivo [`updates.md`](../updates.md) para manter a equipe em sincronia.
