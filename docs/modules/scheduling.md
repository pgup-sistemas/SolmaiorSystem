# 🗓️ Módulo Agenda (Scheduling)

## 1. Objetivo do Módulo
Centralizar a gestão de horários de aulas, salas, professores e eventos especiais (ensaio, recital, workshop). Garante que não haja conflitos de agenda e oferece visualização clara para todos os perfis.

---

## 2. Acesso e Permissões
| Perfil | Permissões |
|--------|------------|
| **Aluno** | Visualizar aulas próprias e eventos confirmados |
| **Professor** | Visualizar agenda própria, propor reagendamentos, confirmar presença |
| **Secretaria** | Criar/editar eventos, resolver conflitos, agendar trial lessons |
| **Administrador** | Acesso total, configuração de horários padrão, auditoria |

---

## 3. Principais Componentes
- **Calendário Global**: visão agregada por dia, semana ou mês.
- **Calendário por Recurso**: agenda por sala, professor ou instrumento.
- **Gerenciamento de Conflitos**: painel para detectar sobreposições.
- **Aulas Experimentais**: integração com fluxo de confirmação por token.
- **Eventos Especiais**: recitais, workshops, provas práticas.

---

## 4. Passo a Passo de Uso

### 4.1 Criar aula ou evento
1. Vá em **Agenda > Novo Evento**.
2. Preencha tipo, data, hora inicial/final, professor, sala e participantes.
3. O sistema alerta automaticamente sobre conflitos.
4. Confirme para notificar envolvidos.

![Placeholder](../static/screenshots/scheduling-create-event.png)

### 4.2 Resolver conflito
1. Abra **Agenda > Conflitos**.
2. Clique no conflito listado (ex.: mesma sala reservada).
3. Escolha uma solução: realocar sala, mudar horário ou notificar responsável.
4. Registre a ação tomada para histórico.

### 4.3 Visualizar agenda pessoal
- **Aluno:** Agenda filtrada com aulas confirmadas, reposições e recitais.
- **Professor:** Agenda com aulas, ensaios e aulas experimentais designadas.
- **Secretaria/Admin:** acesso ao calendário completo com filtro por unidade.

### 4.4 Reagendar aula
1. Selecione a aula no calendário.
2. Clique em **Reagendar**.
3. Informe novos horário/sala.
4. Sistema notifica automaticamente aluno(s) e professor.

---

## 5. Workflow da Agenda
```
Criação/Ajuste de Evento → Checagem automática de conflito
                     → Confirmação e notificação por email/app
                     → Registro em logs de auditoria
```

---

## 6. Erros Comuns e Como Resolver
| Situação | Causa | Solução |
|----------|-------|---------|
| Evento não aparece para o aluno | Aula com status rascunho | Mudar status para confirmado |
| Professor em duas salas no mesmo horário | Falha na checagem manual | Reabra conflito e ajuste recurso |
| Notificação não enviada | Integração de email offline | Checar fila de tarefas (Celery/Redis) |

---

## 7. Integrações
- **Acadêmico**: gera eventos automaticamente após matrícula.
- **Financeiro**: exibe alertas para alunos inadimplentes (opcional).
- **Recitais**: cria blocos de agenda reservados por evento.

---

## 8. Relatórios
- **Utilização de Salas**.
- **Carga horária por professor**.
- **Pontualidade de aulas experimentais**.

---

## 9. Checklist Operacional
- [ ] Confirmar agenda semanal com professores.
- [ ] Verificar conflitos remanescentes diariamente.
- [ ] Validar agendamentos automáticos de reposição.

---

## 10. Atualizações Futuras
- Integração com calendários externos (Google, Outlook).
- Visão mobile dedicada com arraste e solta.

Registre novas funcionalidades em [`updates.md`](../updates.md).
