# ⚙️ Módulo Configurações & Administração

## 1. Objetivo do Módulo
Concentrar parâmetros globais do sistema Sol Maior, incluindo gerenciamento de usuários, permissões, integrações externas, calendários acadêmicos e políticas institucionais.

---

## 2. Acesso e Permissões
| Perfil | Permissões |
|--------|------------|
| **Administrador** | Acesso completo, criação e edição de configurações |
| **Secretaria** | Acesso limitado (ex.: calendários, templates de comunicação) |
| **Financeiro** | Ajuste de configurações financeiras (quando delegado) |
| **Professor/Aluno** | Sem acesso (apenas configurações pessoais em seus perfis) |

---

## 3. Estrutura do Módulo
- **Usuários & Permissões**: cadastro de contas, papéis, políticas de acesso.
- **Calendário Acadêmico**: definição de ano letivo, recessos e eventos oficiais.
- **Parâmetros Financeiros**: planos de pagamento, descontos, integrações com gateways.
- **Integrações**: SMTP, APIs externas, plataformas pedagógicas.
- **Templates de Comunicação**: modelos de email, SMS, notificações automáticas.

---

## 4. Passo a Passo de Uso

### 4.1 Cadastrar usuário e atribuir perfil
1. Acesse **Configurações > Usuários & Permissões**.
2. Clique em **Novo usuário**.
3. Informe dados básicos (nome, e-mail, telefone, unidade).
4. Selecione o *role* (perfil). Perfis padrão: aluno, professor, secretaria, admins.
5. Defina permissões adicionais se necessário (ex.: acesso a relatórios).
6. Salve para enviar convite por email.

![Placeholder](../static/screenshots/settings-users.png)

### 4.2 Configurar calendários acadêmicos
1. Vá em **Configurações > Calendário**.
2. Crie ou edite o período letivo (ex.: 2025/1).
3. Adicione feriados, recessos e datas importantes.
4. Clique em **Aplicar** para atualizar módulos Acadêmico e Agenda.

### 4.3 Ajustar parâmetros financeiros
1. Acesse **Configurações > Financeiro**.
2. Defina política de reajuste, multas, juros e descontos.
3. Configure gateways de pagamento (cartão, PIX, boleto).
4. Teste integração enviando cobrança de exemplo.

### 4.4 Gerenciar integrações
- Localize **Configurações > Integrações**.
- Adicione APIs externas (CRM, assinatura eletrônica, BI).
- Use o modo teste antes de ativar em produção.
- Habilite alertas para falhas de integração (logs).

---

## 5. Workflow de Configuração
```
Definir perfis → Ajustar permissão → Configurar calendários/financeiro
            → Validar integrações → Monitorar logs e auditorias
```

---

## 6. Erros Comuns e Soluções
| Situação | Causa provável | Solução |
|----------|----------------|---------|
| Usuário sem acesso a módulo | Role sem permissão atribuída | Revisar Role em Usuários & Permissões |
| E-mail não enviado | SMTP mal configurado | Revisar credenciais e teste com envio de e-mail |
| Calendário não atualiza | Cache do navegador | Limpar cache ou forçar recarregamento |
| Gateway de pagamento falha | Chave expirada | Renovar credenciais e revalidar |

---

## 7. Auditoria e Logs
- Acesse **Configurações > Auditoria** para revisar alterações.
- Logs críticos (financeiro, permissão, integração) são auditáveis.
- Exporte relatórios para CSV em caso de auditoria externa.

### Política de logs
- **Críticos:** guardados por 5 anos.
- **Operacionais:** 2 anos.

---

## 8. Checklist de Boas Práticas
- [ ] Revisar permissões mensalmente.
- [ ] Validar calendário do próximo semestre com antecedência.
- [ ] Testar integrações após atualizações do sistema.
- [ ] Manter documentação do SMTP e APIs atualizada.

---

## 9. Atualizações Futuras
- Sincronização com plataformas externas de LMS/ERP.
- Delegação granular de permissões (por campo).
- Backups automáticos dos parâmetros.

> Registre todas as mudanças relevantes em [`updates.md`](../updates.md) para fins de auditoria e compartilhamento com a equipe.
