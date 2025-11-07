# 🎓 Módulo Acadêmico

## 1. Objetivo do Módulo
Gerenciar toda a jornada acadêmica do aluno: matrículas, turmas, aulas regulares, reposições e acompanhamento pedagógico.

---

## 2. Acesso e Permissões
| Perfil | Permissões |
|--------|------------|
| **Aluno** | Visualização das próprias aulas, materiais e feedbacks |
| **Professor** | Registro de presença, feedback, upload de materiais |
| **Secretaria** | Gestão de turmas, matrículas, reposições, histórico acadêmico |
| **Administrador** | Acesso total, auditoria, configurações globais |

---

## 3. Estrutura do módulo
- **Turmas**: cadastro de grupos por instrumento/professor.
- **Alunos**: ficha individual com dados acadêmicos, financeiro e histórico.
- **Aulas**: agenda semanal/mensal com status (agendada, concluída, cancelada).
- **Reposições**: workflow de solicitação, aprovação e acompanhamento.
- **Materiais Didáticos**: biblioteca com controle de acesso por turma.

---

## 4. Passo a Passo de Uso

### 4.1 Criar turma
1. Acesse **Acadêmico > Turmas**.
2. Clique em **Nova turma**.
3. Defina instrumento, professor, nível e capacidade.
4. Salve e associe alunos.

![Placeholder](../static/screenshots/academic-create-class.png)

### 4.2 Matricular aluno em turma
1. Abra a ficha do aluno em **Acadêmico > Alunos**.
2. Clique em **Adicionar turma**.
3. Selecione plano e forma de pagamento (integrado ao Financeiro).
4. Confirme para que a agenda seja gerada automaticamente.

### 4.3 Registrar presença
1. Professor acessa **Minha Agenda**.
2. Seleciona aula > **Registrar presença**.
3. Marca presentes/ausentes, inclui observações.
4. Salva e sincroniza com relatório acadêmico.

### 4.4 Gerenciar reposições
1. Solicitação do aluno via portal.
2. Secretaria recebe notificação e avalia justificativa.
3. Ao aprovar, sugere datas alternativas (agenda integrada).
4. Registro final aparece na timeline do aluno e professor.

---

## 5. Fluxo de Trabalho (Workflow)
```
Cadastro de aluno → Definição de plano → Matrícula → Agenda automática
                  ↘ Solicitação de reposição → Aprovação → Nova aula
```

> **Integrações:** o módulo conecta-se com Financeiro (planos e faturas), Agenda (horários) e Relatórios (indicadores de presença).

---

## 6. Erros Comuns e Soluções
| Erro | Causa provável | Correção |
|------|----------------|----------|
| Aula sem professor | Professor removido da turma | Atualize a configuração da turma ou substitua o professor |
| Reposição não aparece | Não foi aprovada pela secretaria | Verifique status em **Reposições** |
| Material indisponível | Permissão incorreta | Ajuste permissões em **Materiais > Configurações** |

---

## 7. Relatórios Disponíveis
- **Frequência por aluno/turma**.
- **Progresso pedagógico (feedbacks)**.
- **Solicitações de reposição aprovadas/pendentes**.

---

## 8. Checklist de Auditoria Acadêmica
- [ ] Turmas com capacidade correta
- [ ] Professores associados corretamente
- [ ] Logs de presença consistentes
- [ ] Materiais atualizados por nível

---

## 9. Referências Cruzadas
- [Manual do Professor](../user-guides/teacher.md)
- [Manual do Aluno](../user-guides/student.md)
- [Módulo Financeiro](finance.md)
- [Glossário](../glossary.md)

---

## 10. Atualizações Futuras
- Espaço reservado para novas funcionalidades, integração com plataformas EAD ou relatórios personalizados.

> Registre qualquer atualização em [`updates.md`](../updates.md).
