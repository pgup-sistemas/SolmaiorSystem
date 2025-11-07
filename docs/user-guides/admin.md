# 🛡️ Manual do Administrador

## 1. Objetivo
Este manual apresenta as responsabilidades e ferramentas disponíveis para administradores da plataforma Sol Maior. Administradores possuem visão global do sistema e controle sobre módulos críticos, permissões e integrações.

---

## 2. Acesso e Autenticação
1. Acesse `https://solmaior.com.br/app/admin`.
2. Entre com suas credenciais administrativas.
3. Autenticação em dois fatores é obrigatória (via aplicativo autenticador ou token enviado por email).
4. Revise o log de acessos recentes exibido na tela inicial para garantir que não existam entradas suspeitas.

> **Procedimento de segurança:** caso perca o acesso ao 2FA, contate imediatamente a equipe de infraestrutura. Não compartilhe seu token com outros usuários.

---

## 3. Dashboard Executivo
![Placeholder](../static/screenshots/admin-dashboard.png)

### 3.1 Principais cards
- **Visão financeira**: faturamento mensal, inadimplência, projeções.
- **Indicadores acadêmicos**: ocupação por instrumento, taxa de presença, churn.
- **Trial Lessons**: conversão de leads e status de confirmações.
- **Alertas críticos**: falhas em integrações, serviços interrompidos, auditorias pendentes.

### 3.2 Ações rápidas
| Ação | Descrição |
|------|-----------|
| **Criar usuário** | Adicionar novos usuários com permissões específicas |
| **Configurar períodos letivos** | Definir calendários acadêmicos anuais/semestrais |
| **Gerenciar integrações** | API Keys, SMTP, gateways de pagamento |
| **Revisar auditorias** | Aprovar ou rejeitar lançamentos financeiros sensíveis |

---

## 4. Gerenciamento de Usuários e Permissões
1. Abra **Configurações > Usuários & Permissões**.
2. Pesquise por usuário ou filtre por role.
3. Utilize a aba **Perfis** para criar ou editar papéis (aluno, professor, secretaria, admin, financeiro etc.).
4. Defina permissões granulares (CRUD por módulo, exportação, visualização de dados sensíveis).
5. Gere logs de alteração para auditoria.

> **Erro comum:** Duplicidade de email. Use o campo *Unificar contas* para mesclar registros antes de remover um usuário.

---

## 5. Configurações Globais
- **Calendário Acadêmico:** defina períodos letivos, recessos, datas de recital e feriados.
- **Parâmetros Financeiros:** configure planos, índices de reajuste, políticas de desconto.
- **Integrações Externas:** SMTP, provedores de pagamento, CRM externo.
- **Notificações:** controle padrões de e-mail, lembretes e fluxos automatizados.

![Placeholder](../static/screenshots/admin-settings.png)

### Checklist de lançamento
- [ ] Definir ano letivo
- [ ] Atualizar tabela de instrumentos/salas
- [ ] Revisar políticas de reposição
- [ ] Validar SMTP e disparos de e-mail

---

## 6. Auditoria e Segurança
- Acesse **Auditoria > Logs** para revisar ações críticas (ajustes financeiros, alterações de matrícula, exclusões).
- Utilize filtros (por usuário, período, tipo de ação) para investigação.
- Gere relatórios exportáveis em caso de auditoria externa.

### Política de Retenção
- Logs críticos: 5 anos
- Logs operacionais: 2 anos

> **Dica:** Agende alertas automáticos para eventos suspeitos (ex.: múltiplas exclusões em sequência).

---

## 7. Relatórios & Indicadores Avançados
1. Vá em **Relatórios > Inteligência**.
2. Utilize dashboards pré-configurados (financeiro, acadêmico, marketing).
3. Para análises personalizadas, exporte dados em CSV/JSON ou conecte via API (quando habilitada).
4. Configure alertas por email para limites (ex.: ocupação < 60%, churn > 10%).

---

## 8. Gestão de Conteúdo Público
- Em **Landing Page > Conteúdo**, atualize textos, imagens, seções (sobre, depoimentos, destaque).
- Em **Blog & Notícias**, programe publicações e destaque materiais.
- Monitore a performance dos CTAs (solicitar aula experimental, falar com a secretaria).

---

## 9. Processos Críticos
| Processo | Frequência | Responsável | Observações |
|----------|------------|-------------|-------------|
| Backup do banco | Diário | TI | Validar integridade semanalmente |
| Revisão de permissões | Mensal | Administração | Remover ex-colaboradores |
| Fechamento financeiro | Mensal | Financeiro + Admin | Conferir auditoria |
| Atualização da landing | Mensal ou conforme campanhas | Marketing | Coordenação com secretaria |

---

## 10. Perguntas Frequentes do Administrador
| Pergunta | Resposta |
|----------|----------|
| **Como restaurar um cadastro excluído?** | Use Auditoria > Recuperar Registro (disponível por 30 dias) |
| **Consigo clonar uma configuração de API?** | Sim, em Integrações > Clonar credenciais |
| **Posso editar um log?** | Não. Logs são imutáveis por segurança |

Consulte o [FAQ geral](../faq.md) para dúvidas compartilhadas entre perfis.

---

## 11. Contato direto com a TI
- **Email:** tecnologia@solmaior.com.br
- **Canal urgente:** pager interno / número de plantão
- **Base de conhecimento técnica:** disponível no repositório privado da TI

> **Mantenha este manual** atualizado a cada mudança de configuração ou inclusão de novo módulo. Registre as alterações em [`updates.md`](../updates.md).
