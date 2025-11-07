# ✉️ Módulo de Comunicações & Notificações

## 1. Objetivo do Módulo
Gerenciar mensagens internas e externas da Escola Sol Maior: e-mails transacionais, campanhas, avisos institucionais e notificações automatizadas para alunos, professores, secretaria e responsáveis.

---

## 2. Acesso e Permissões
| Perfil | Permissões |
|--------|------------|
| **Aluno/Responsável** | Receber notificações, configurar preferências |
| **Professor** | Enviar mensagens para turmas, receber avisos administrativos |
| **Secretaria** | Disparar comunicados, newsletters e mensagens operacionais |
| **Administrador** | Configurar templates, políticas de envio, integrações |

---

## 3. Componentes Principais
- **Mensagens Transacionais**: emails automáticos disparados por eventos (aula agendada, pagamento confirmado, link de confirmação de trial lesson).
- **Campanhas**: ferramentas de email marketing para eventos, matrículas e recitais.
- **Avisos Internos**: mural digital para comunicados rápidos.
- **Preferências de Notificação**: painel para configurar canais (email, SMS, push) e horários de silêncio.
- **Templates**: biblioteca de modelos reutilizáveis com campos dinâmicos.

---

## 4. Passo a Passo de Uso

### 4.1 Disparar comunicado em massa
1. Acesse **Comunicações > Campanhas**.
2. Clique em **Nova Campanha**.
3. Selecione público alvo (ex.: alunos iniciantes, responsáveis inadimplentes).
4. Escolha um template existente ou crie um do zero.
5. Agende o disparo ou envie imediatamente.
6. Acompanhe taxa de abertura e cliques em **Resultados**.

![Placeholder](../static/screenshots/communications-campaign.png)

### 4.2 Configurar e-mails transacionais
1. Vá para **Comunicações > Transacionais**.
2. Selecione o evento (ex.: aula experimental agendada).
3. Edite texto, campos dinâmicos e remetente.
4. Salve e teste com envio para um email interno.

### 4.3 Ajustar preferências do usuário
- Secretarias podem orientar alunos/professores a acessar **Meu Perfil > Notificações** para habilitar canais ou definir horários de silêncio.
- Administradores podem importar configurações em massa via CSV.

### 4.4 Monitorar fila de envio
1. Em **Comunicações > Monitoramento**, veja mensagens pendentes/entregues.
2. Verifique status de integrações (SMTP, SMS, push).
3. Reenvie manualmente caso necessário.

---

## 5. Workflow de Notificações
```
Evento (ex.: aula agendada) → Sistema gera mensagem → Aplica template
                           → Envia via canal configurado → Usuário recebe/loga
```

---

## 6. Erros Comuns e Soluções
| Problema | Causa | Solução |
|----------|-------|---------|
| Email não entregue | SMTP com credenciais inválidas | Revalide SMTP em Configurações |
| Mensagem duplicada | Evento disparado duas vezes | Checar logs e deduplicação |
| Usuário não recebe | Preferência desabilitada ou horário de silêncio | Orientar usuário a ajustar preferências |

---

## 7. Integrações
- **SMTP / Serviços de Email**: SendGrid, Amazon SES, Outlook.
- **SMS / WhatsApp** (quando habilitado): Twilio, Zenvia.
- **Push Notifications**: integração com apps móveis (roadmap).
- **BI/Relatórios**: estatísticas de abertura, cliques e entregabilidade.

---

## 8. Relatórios de Comunicação
- Taxa de entrega por campanha.
- Engajamento por tipo de mensagem.
- Relatório de opt-in/opt-out.
- Tempo médio de resposta a notificações críticas.

---

## 9. Checklist Operacional
- [ ] Validar templates antes de campanhas importantes.
- [ ] Revisar configurações de horários de silêncio trimestralmente.
- [ ] Monitorar entregabilidade após atualizações de SMTP.
- [ ] Manter lista de destinatários sincronizada com o módulo Acadêmico.

---

## 10. Atualizações Futuras
- Integração com chatbots e atendimento omnichannel.
- Personalização avançada com dados de comportamento.
- Análise de sentimento em respostas.

> Documente evoluções do módulo em [`updates.md`](../updates.md) para garantir rastreabilidade.
