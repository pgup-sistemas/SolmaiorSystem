# 📌 Visão Geral do Sistema Sol Maior

## 🎯 Missão do Sistema
A plataforma Sol Maior é um sistema integrado para gestão de escolas de música. Foi inspirada no fluxo de trabalho de instituições com múltiplos departamentos (acadêmico, administrativo/financeiro e marketing) e atende desde o primeiro contato de um aluno em potencial até o acompanhamento de performances e indicadores.

## 👥 Público-Alvo
| Perfil | Objetivo Principal | Funcionalidades-chave |
|--------|-------------------|------------------------|
| **Alunos e Responsáveis** | Acompanhar aulas, agenda, pagamentos e recitais | Painel do aluno, calendário, faturas, materiais de estudo |
| **Professores** | Gerenciar agenda, presença e materiais | Agenda docente, registro de aulas, feedback, relatórios|
| **Secretaria** | Controlar inscrições, matrículas, comunicação | Funil de aquisição (trial lessons), cadastro, emissão de documentos |
| **Administradores** | Supervisionar toda a operação | Dashboard executivo, KPIs, configurações globais, auditoria |

## 🧱 Arquitetura de Módulos
A plataforma é dividida em componentes independentes, porém sincronizados por permissões e fluxos de dados.

### Módulos Principais
1. **Acadêmico (Aulas & Alunos)**
   - Gestão de matrículas, aulas regulares, reposições e presenças.
   - Ferramentas de acompanhamento individual.
2. **Agenda (Scheduling)**
   - Gestão de salas, professores e horários.
   - Workflows específicos para aulas experimentais e recitais.
3. **Financeiro**
   - Cobranças recorrentes, geração de faturas, controle de inadimplência e auditoria.
4. **Recitais & Performances**
   - Organização de eventos, inscrições, roteiros e feedback pós-performance.
5. **Landing Page & Marketing**
   - Conteúdo público, conversão de leads, formulários de aulas experimentais.
6. **Configurações & Segurança**
   - Gestão de papéis (roles), permissões, auditoria e integrações.
7. **Relatórios & Indicadores**
   - Painéis analíticos, previsões de ocupação, indicadores de evasão e relatórios financeiros.
8. **Comunicações & Notificações**
   - Automação de emails, lembretes e mensagens internas.

## 🧭 Fluxo Macro do Sistema
```
Visitante → Se interessa pela escola → (Landing Page)
         → Solicita aula experimental → (Trial Lessons)
         → Atendimento da Secretaria → (Aprovação/Agendamento)
         → Conversão em aluno → (Acadêmico + Financeiro)
         → Acompanhamento contínuo → (Agenda, Relatórios, Recitais)
```

## 💡 Principais Diferenciais
- **Workflows automatizados**: e-mails, confirmações, lembretes.
- **Integração total** entre agenda, financeiro e acadêmico.
- **Indicadores inteligentes**: dashboards com métricas de ocupação, churn e receita.
- **Experiência multi-perfil**: interfaces específicas para aluno, professor, secretaria e administrador.
- **Segurança e rastreabilidade**: controle de permissões com auditoria de ações sensíveis.

## 🛠 Tecnologias Utilizadas
| Camada | Tecnologias |
|--------|-------------|
| Backend | Flask, SQLAlchemy, Celery (tarefas assíncronas), Flask-Login |
| Frontend | Jinja2, TailwindCSS/Bootstrap customizado, componentes JS|
| Infraestrutura | SQLite/PostgreSQL (adaptável), Redis (fila de tarefas), integração com SMTP |
| Observabilidade | Logs estruturados, auditoria financeira, relatórios customizados |

## 📈 Visão Geral das Integrações
- **Email Transacional**: envio de confirmações de aulas experimentais, cobranças e atualizações.
- **Sistemas Legados** (opcional): rotinas de importação/exportação em CSV.
- **APIs** (em roadmap): exposição de dados para parceiros e dashboards externos.

## 🔒 Segurança & Compliance
- Autenticação baseada em papéis (Role-Based Access Control).
- Auditoria financeira com trilhas de aprovação.
- Política de atualização contínua via registro em [`updates.md`](../updates.md).
- Recomendações de backup e replicação em ambientes produtivos.

## 📄 Referências Cruzadas
- Para termos técnicos consulte o [Glossário](../glossary.md).
- Para instruções específicas por perfil vá para [Guias de Usuário](../user-guides/).
- Para processos detalhados acesse a [Documentação de Módulos](../modules/).

---

> **Nota:** Este documento é o ponto de partida para qualquer profissional que esteja começando a utilizar ou administrar o Sistema Sol Maior.
