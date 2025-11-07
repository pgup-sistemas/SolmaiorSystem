# 🎤 Módulo de Recitais & Performances

## 1. Objetivo do Módulo
Organizar eventos artísticos, recitais internos/externos e performances dos alunos, controlando inscrições, repertórios, logística e feedback pós-evento.

---

## 2. Acesso e Permissões
| Perfil | Permissões |
|--------|------------|
| **Aluno** | Inscrever-se em recitais, enviar repertório, visualizar cronograma |
| **Professor** | Indicar alunos, aprovar repertório, registrar feedbacks |
| **Secretaria** | Coordenação geral, logística, comunicação com responsáveis |
| **Administrador** | Configuração de temporadas, relatórios de desempenho |

---

## 3. Estrutura do Módulo
- **Calendário de Recitais**: lista de eventos por temporada ou mês.
- **Inscrições**: painel com alunos inscritos, status e repertório proposto.
- **Roteiro do Evento**: ordem de apresentações, duração estimada e responsável.
- **Feedback Pós-Evento**: formulário para professores e coordenadores.
- **Relatórios**: participação, desempenho, engajamento por turma.

---

## 4. Passo a Passo de Uso

### 4.1 Criar um recital
1. Acesse **Recitais > Novo Recital**.
2. Preencha nome, data, local, público-alvo e capacidade.
3. Defina categorias (iniciantes, intermediário, avançado).
4. Configure regras de inscrição (por professor, autoinscrição ou convite).

![Placeholder](../static/screenshots/recital-create.png)

### 4.2 Inscrição de alunos
- **Alunos**: inscrevem-se via portal, selecionam repertório e enviam anotações.
- **Professores**: recomendam alunos em **Recitais > Indicações**.
- **Secretaria**: confirma inscrições, ajusta horário e envia convites/instruções.

### 4.3 Organizar o roteiro
1. Em **Recitais > Roteiro**, arraste os participantes para definir ordem de apresentação.
2. Informe tempo estimado e recursos necessários (microfone, piano, partituras).
3. Exporte roteiro em PDF para distribuição no evento.

### 4.4 Feedback pós-evento
- Professores preenchem formulário com notas técnicas e observações.
- Coordenadores registram pontos fortes e melhorias para eventos futuros.
- Feedback fica disponível na ficha do aluno (integração com Acadêmico).

---

## 5. Workflow do Evento
```
Criação → Divulgação → Inscrições/Indicações → Confirmação → Execução do evento
                                               ↘ Feedbacks → Relatórios e métricas
```

---

## 6. Erros Comuns e Soluções
| Situação | Motivação | Solução |
|----------|-----------|---------|
| Aluno com repertório incompleto | Não enviou arquivo ou link | Notifique o aluno via sistema (template pronto) |
| Recital lotado antes do previsto | Capacidade limitada | Ative lista de espera ou abra nova sessão |
| Feedback não salvo | Sessão expirada | Habilite salvamento automático (Configurações > Recitais) |

---

## 7. Relatórios
- **Participação por instrumento**.
- **Avaliação média por professor**.
- **Tempo total de evento vs. planejado**.

---

## 8. Integrações
- **Agenda**: bloqueia horários para ensaios e eventos.
- **Acadêmico**: associa performances ao histórico do aluno.
- **Comunicações**: envio de convites e certificados.

---

## 9. Checklist Pré-Evento
- [ ] Confirmar local e equipamentos.
- [ ] Enviar roteiro final aos professores e músicos de apoio.
- [ ] Disponibilizar material gráfico (cartazes, passagens).
- [ ] Checar lista de presença e acessibilidade.

---

## 10. Atualizações Futuras
- Integração com plataformas de transmissão ao vivo.
- Geração automática de certificados com QR Code.
- Avaliação do público com enquetes pós-evento.

> Registre avanços no arquivo [`updates.md`](../updates.md) para manter o histórico do módulo.
