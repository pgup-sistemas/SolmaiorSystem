# 🌐 Módulo Landing Page & Marketing

## 1. Objetivo do Módulo
Captar novos alunos e divulgar a Escola de Música Sol Maior por meio de uma landing page dinâmica, conteúdo institucional e gatilhos para conversão (aulas experimentais, contato, newsletter).

---

## 2. Acesso e Permissões
| Perfil | Permissões |
|--------|------------|
| **Visitante** | Visualizar conteúdo público, solicitar aula experimental |
| **Secretaria/Marketing** | Editar textos, depoimentos, FAQs públicos, publicar notícias |
| **Administrador** | Gerenciar estrutura, SEO, integrações de marketing |

---

## 3. Componentes da Landing Page
- **Seção Hero**: apresentação da marca, vídeo institucional.
- **Destaques de Cursos**: catálogo resumido dos principais instrumentos e modalidades.
- **Depoimentos**: carrossel de alunos e responsáveis.
- **CTA Principal**: formulário de aula experimental (Trial Lesson).
- **Notícias/Blog**: posts sobre eventos e conteúdos educativos.
- **Footer**: informações de contato, redes sociais e políticas.

---

## 4. Passo a Passo de Uso

### 4.1 Atualizar Conteúdo
1. Acesse **Landing Page > Conteúdo**.
2. Edite textos, imagens e chamadas por seção.
3. Clique em **Pré-visualizar** antes de publicar.
4. Publique para aplicar as alterações imediatamente.

![Placeholder](../static/screenshots/landing-edit.png)

### 4.2 Gerenciar CTAs
- Configure botões (ex.: "Solicite sua aula gratuita") com direcionamentos específicos.
- Consulte estatísticas de cliques em **Landing Page > Métricas**.
- Integração com CRM opcional via Webhooks.

### 4.3 Formular de Aula Experimental
1. Acesse **Landing Page > Formulários**.
2. Garanta que os campos obrigatórios (nome, email, telefone, instrumento) estejam ativos.
3. Defina e-mails para notificação (Secretaria/Marketing).
4. Teste o fluxo para verificar envio de emails automáticos.

---

## 5. Workflow do Marketing Digital
```
Campanha → Visitante acessa landing → Preenche formulário
                                      → Recebe e-mail de confirmação automático
                                      → Secretaria recebe lead para contato
```

---

## 6. Erros Comuns
| Problema | Causa | Solução |
|----------|-------|---------|
| Formulário não envia | API de email inativa | Verificar configuração SMTP e fila de tarefas |
| Imagem não atualiza | Cache do navegador/CDN | Limpar cache ou invalidar CDN |
| CTA com link errado | Copy/paste incorreto | Revisar URL e publicar novamente |

---

## 7. Métricas de Marketing
- Taxa de conversão por campanha.
- Origem de tráfego (UTM).
- Taxa de inscrição em aulas experimentais.
- Variação de engajamento por sessão.

---

## 8. Integrações Disponíveis
- **Analytics**: Google Analytics/Tag Manager.
- **CRM**: Webhooks para RD Station, HubSpot ou outros.
- **Email Marketing**: Mailchimp, Sendgrid (via API key).

---

## 9. Checklist de Publicação
- [ ] Revisar ortografia e links.
- [ ] Otimizar imagens (peso e títulos alternativos).
- [ ] Atualizar depoimentos e fotos.
- [ ] Testar formulário e e-mails automáticos.
- [ ] Atualizar SEO (title, meta description, keywords).

---

## 10. Atualizações Futuras
- Implantar testes A/B para CTAs.
- Integrar chatbot para atendimento inicial.
- Adicionar seção de vídeos de performances.

> Registre mudanças relevantes no arquivo [`updates.md`](../updates.md).
