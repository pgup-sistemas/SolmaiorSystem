# Integração com Stripe - Sistema Sol Maior

## Visão Geral

O sistema Sol Maior está integrado com o Stripe para processar pagamentos online de mensalidades. A integração oferece:

- ✅ Pagamentos seguros com cartão de crédito
- ✅ Interface moderna com Stripe Checkout
- ✅ Atualização automática de status via webhooks
- ✅ Conformidade com PCI DSS (dados de cartão não armazenados)
- ✅ Suporte a múltiplas moedas (configurado para BRL)

## Configuração Inicial

### 1. Criar Conta no Stripe

1. Acesse [stripe.com](https://stripe.com) e crie uma conta
2. Complete o processo de verificação da conta
3. Acesse o Dashboard do Stripe

### 2. Obter Chaves de API

No Dashboard do Stripe:

1. Clique em "Developers" > "API keys"
2. Você verá duas chaves:
   - **Publishable key** (pk_test_... para teste, pk_live_... para produção)
   - **Secret key** (sk_test_... para teste, sk_live_... para produção)

⚠️ **IMPORTANTE**: Nunca compartilhe ou exponha suas chaves secretas!

### 3. Configurar Variáveis de Ambiente no Replit

As seguintes variáveis de ambiente precisam ser configuradas:

- `STRIPE_PUBLIC_KEY`: Sua chave pública do Stripe
- `STRIPE_SECRET_KEY`: Sua chave secreta do Stripe
- `STRIPE_WEBHOOK_SECRET`: Segredo do webhook (configurar depois)

### 4. Configurar Webhooks

Os webhooks permitem que o Stripe notifique o sistema sobre eventos de pagamento:

1. No Dashboard do Stripe, vá para "Developers" > "Webhooks"
2. Clique em "Add endpoint"
3. Configure a URL do webhook:
   - Para produção: `https://SEU_DOMINIO/payments/webhook`
   - Para teste: use o Stripe CLI (veja abaixo)
4. Selecione os eventos:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `checkout.session.completed`
5. Copie o "Signing secret" (whsec_...)
6. Adicione como `STRIPE_WEBHOOK_SECRET` nas variáveis de ambiente

## Arquitetura da Integração

### Modelos de Dados

#### Student
```python
stripe_customer_id: String  # ID do cliente no Stripe
```

#### Payment
```python
stripe_customer_id: String          # ID do cliente
stripe_payment_intent_id: String    # ID do payment intent
stripe_charge_id: String            # ID da cobrança
stripe_payment_method_id: String    # ID do método de pagamento
stripe_status: String               # Status no Stripe
stripe_client_secret: String        # Client secret
stripe_webhook_received: Boolean    # Se webhook foi recebido
stripe_error_message: Text          # Mensagem de erro
```

### Fluxo de Pagamento

1. **Aluno acessa página de pagamento**
   - Route: `GET /payments/payment/<payment_id>`
   - Exibe detalhes do pagamento e botão de pagar

2. **Aluno clica em "Pagar"**
   - JavaScript chama `POST /payments/payment/<payment_id>/checkout`
   - Backend cria sessão do Stripe Checkout
   - Usuário é redirecionado para página segura do Stripe

3. **Processamento do Pagamento**
   - Stripe processa o pagamento
   - Usuário é redirecionado de volta:
     - Sucesso: `/payments/success?payment_id=X`
     - Cancelamento: `/payments/cancel?payment_id=X`

4. **Confirmação via Webhook**
   - Stripe envia webhook para `/payments/webhook`
   - Sistema atualiza status do pagamento automaticamente
   - Aluno e secretaria são notificados (futuro)

### Serviços Principais

#### `StripeService`

Localizado em `app/services/stripe_service.py`:

```python
class StripeService:
    def get_or_create_customer(student_id)        # Cria/recupera cliente
    def create_payment_intent(payment_id)         # Cria payment intent
    def create_checkout_session(payment_id)       # Cria sessão de checkout
    def handle_webhook(payload, sig_header)       # Processa webhooks
    def get_payment_status(payment_id)            # Consulta status
    def cancel_payment_intent(payment_id)         # Cancela pagamento
```

### Rotas de API

#### Públicas (com autenticação)

- `GET /payments/payment/<id>` - Detalhes do pagamento
- `POST /payments/payment/<id>/checkout` - Criar checkout
- `POST /payments/payment/<id>/payment-intent` - Criar payment intent
- `GET /payments/payment/<id>/status` - Status do pagamento
- `GET /payments/success` - Página de sucesso
- `GET /payments/cancel` - Página de cancelamento

#### Administrativas

- `POST /payments/payment/<id>/cancel` - Cancelar pagamento (admin/secretary)

#### Webhooks

- `POST /payments/webhook` - Endpoint para webhooks do Stripe

## Segurança

### Proteções Implementadas

1. **Validação de Assinatura de Webhooks**
   - Usa `STRIPE_WEBHOOK_SECRET` para verificar autenticidade
   - Rejeita requisições não autorizadas

2. **Autorização**
   - Alunos só podem ver/pagar suas próprias mensalidades
   - Admin/Secretaria têm acesso completo

3. **Dados de Cartão**
   - Nunca armazenados no sistema
   - Processados diretamente pelo Stripe (PCI compliant)

4. **HTTPS Obrigatório**
   - Todas as comunicações com Stripe usam HTTPS
   - Webhooks requerem HTTPS em produção

### Configurações de Segurança

```python
# config.py
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
```

## Testes

### Modo de Teste

Use as chaves de teste (começam com `pk_test_` e `sk_test_`) para testar sem cobranças reais.

### Cartões de Teste

O Stripe fornece cartões de teste:

- **Sucesso**: 4242 4242 4242 4242
- **Falha**: 4000 0000 0000 0002
- **3D Secure**: 4000 0025 0000 3155

Detalhes:
- **CVV**: Qualquer 3 dígitos
- **Data de Validade**: Qualquer data futura
- **CEP**: Qualquer CEP válido

### Testar Webhooks Localmente

Use o Stripe CLI:

```bash
# Instalar Stripe CLI
# https://stripe.com/docs/stripe-cli

# Login
stripe login

# Encaminhar webhooks para localhost
stripe listen --forward-to localhost:5000/payments/webhook

# Em outro terminal, disparar eventos de teste
stripe trigger payment_intent.succeeded
```

## Monitoramento

### Dashboard do Stripe

Acesse o Dashboard do Stripe para:
- Ver todas as transações
- Monitorar tentativas de pagamento
- Verificar logs de webhooks
- Gerenciar clientes
- Emitir reembolsos

### Logs do Sistema

O sistema registra:
- Criação de payment intents
- Erros de processamento
- Webhooks recebidos
- Falhas de pagamento

Verifique os logs em: `/tmp/logs/Server_*.log`

## Troubleshooting

### Pagamento não atualiza após conclusão

**Causa**: Webhook não está configurado ou não está sendo recebido

**Solução**:
1. Verifique se `STRIPE_WEBHOOK_SECRET` está configurado
2. Teste o webhook no Dashboard do Stripe
3. Verifique os logs de webhook no Stripe

### Erro "Stripe not configured"

**Causa**: `STRIPE_PUBLIC_KEY` ou `STRIPE_SECRET_KEY` não configuradas

**Solução**:
1. Configure as variáveis de ambiente
2. Reinicie a aplicação

### Erro de assinatura do webhook

**Causa**: `STRIPE_WEBHOOK_SECRET` incorreto ou ausente

**Solução**:
1. Verifique o signing secret no Dashboard do Stripe
2. Atualize a variável de ambiente
3. Reinicie a aplicação

## Roadmap

Melhorias futuras planejadas:

- [ ] Suporte a pagamento por Pix
- [ ] Parcelamento com cartão
- [ ] Pagamento recorrente automático
- [ ] Notificações por email após pagamento
- [ ] Relatórios de pagamento
- [ ] Exportação de dados para contabilidade
- [ ] Suporte a cupons de desconto

## Referências

- [Documentação do Stripe](https://stripe.com/docs)
- [Stripe Checkout](https://stripe.com/docs/payments/checkout)
- [Webhooks](https://stripe.com/docs/webhooks)
- [Cartões de Teste](https://stripe.com/docs/testing)
- [API Python](https://stripe.com/docs/api/python)
