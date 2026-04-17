# 🚀 SillientPay Integration Guide

## Overview

The NØVRA e-commerce is fully integrated with SillientPay payment gateway for secure payment processing including Pix, Credit Card, and Boleto.

## Features

- ✅ **Real-time API Integration** - Direct communication with SillientPay API
- ✅ **Webhook Signature Verification** - HMAC-SHA256 signature validation for security
- ✅ **Automatic Order Status Updates** - Webhooks update order status automatically
- ✅ **Fallback to Test Mode** - Graceful degradation if API fails
- ✅ **Production & Sandbox Support** - Easy switching between environments

## Configuration

### Environment Variables

Add these variables to your `.env` file or configure in your deployment platform:

```bash
# Enable SillientPay
SILLIENT_PAY_ENABLED=true

# API Configuration
SILLIENT_PAY_BASE_URL=https://api.sillientpay.com
SILLIENT_PAY_API_KEY=your-production-api-key
SILLIENT_PAY_WEBHOOK_SECRET=your-webhook-secret

# For Sandbox/Testing:
# SILLIENT_PAY_BASE_URL=https://sandbox.sillientpay.com
# SILLIENT_PAY_API_KEY=your-sandbox-api-key
# SILLIENT_PAY_WEBHOOK_SECRET=your-sandbox-webhook-secret
```

### Getting API Credentials

1. **Create SillientPay Account**
   - Visit [sillientpay.com](https://sillientpay.com)
   - Sign up for a merchant account
   - Complete verification process

2. **Generate API Key**
   - Go to Dashboard → Settings → API Keys
   - Click "Generate New Key"
   - Copy the API key
   - Add to `SILLIENT_PAY_API_KEY`

3. **Configure Webhook**
   - Go to Dashboard → Settings → Webhooks
   - Add webhook URL: `https://your-domain.com/pagamento/sillient/callback`
   - Generate webhook secret
   - Add to `SILLIENT_PAY_WEBHOOK_SECRET`

4. **Sandbox Testing**
   - Use sandbox credentials for testing
   - Test all payment flows
   - Verify webhook delivery
   - Switch to production when ready

## API Integration Details

### Create Checkout

When a customer selects SillientPay at checkout:

```python
# The system automatically calls SillientPay API
POST {SILLIENT_PAY_BASE_URL}/v1/checkout

Headers:
  Authorization: Bearer {API_KEY}
  Content-Type: application/json

Body:
  {
    "order_id": "123",
    "amount": 499.90,
    "currency": "BRL",
    "callback_url": "https://your-domain.com/pagamento/sillient/callback",
    "cancel_url": "https://your-domain.com/carrinho",
    "success_url": "https://your-domain.com/checkout/sucesso/123",
    "metadata": {
      "order_id": 123,
      "timestamp": "2026-04-17T14:30:00"
    }
  }

Response:
  {
    "id": "checkout_abc123",
    "reference": "SILLIENT-LIVE-123",
    "checkout_url": "https://checkout.sillientpay.com/checkout_abc123"
  }
```

### Webhook Callback

SillientPay sends payment status updates:

```python
POST /pagamento/sillient/callback

Headers:
  X-Sillient-Signature: {HMAC-SHA256 signature}
  Content-Type: application/json

Body:
  {
    "reference": "SILLIENT-LIVE-123",
    "status": "paid",
    "amount": 499.90,
    "payment_method": "pix",
    "paid_at": "2026-04-17T14:35:00Z"
  }
```

**Security:**
- Signature is verified using HMAC-SHA256
- Invalid signatures are rejected with 401
- Only valid webhooks update order status

## Payment Flow

### 1. Customer Checkout
```
Customer → Checkout → Select SillientPay → Submit Order
```

### 2. Create Payment
```
System → SillientPay API → Create Checkout → Get Checkout URL
```

### 3. Redirect to Payment
```
Customer → Redirect to SillientPay → Complete Payment
```

### 4. Webhook Notification
```
SillientPay → Webhook → System → Update Order Status
```

### 5. Redirect Back
```
SillientPay → Redirect to Success URL → Customer Sees Confirmation
```

## Order Status

| Status | Description |
|--------|-------------|
| `awaiting_payment` | Order created, waiting for payment |
| `paid` | Payment confirmed by SillientPay |
| `cancelled` | Payment cancelled by customer |
| `failed` | Payment failed or rejected |

## Testing

### Sandbox Mode

1. Configure sandbox credentials
2. Set `SILLIENT_PAY_ENABLED=true`
3. Use sandbox API URL
4. Test with test cards/Pix

### Test Payment Methods

**Pix (Sandbox):**
- Use sandbox Pix QR code
- Payment auto-confirms in 30 seconds

**Credit Card (Sandbox):**
- Card number: `4111 1111 1111 1111`
- Expiry: Any future date
- CVV: Any 3 digits
- Result: Success

**Boleto (Sandbox):**
- Generated boleto number
- Payment auto-confirms in 2 minutes

## Troubleshooting

### Webhook Not Received

**Check:**
- Webhook URL is correct and accessible
- Firewall allows SillientPay IPs
- Webhook secret matches
- Signature verification working

**Debug:**
```python
# Enable logging to see webhook attempts
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Payment Not Updating

**Check:**
- Order has correct `payment_reference`
- Webhook signature is valid
- Database connection working
- Order status logic correct

### API Timeout

**Check:**
- SillientPay API is accessible
- Network connectivity
- Timeout value (currently 30s)
- API key is valid

### Fallback to Test Mode

If API fails, system automatically falls back to test mode:
- Customer sees payment preview page
- Manual approval available via admin
- Order marked as `awaiting_payment`

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for all secrets
3. **Rotate API keys** regularly
4. **Enable webhook signature verification**
5. **Use HTTPS** for all webhooks
6. **Monitor webhook failures** for suspicious activity
7. **Keep webhook secret** secure
8. **Log all payment events** for audit trail

## Production Checklist

Before going live:

- [ ] Production API key configured
- [ ] Webhook URL accessible from internet
- [ ] Webhook secret configured
- [ ] SSL certificate installed
- [ ] Firewall allows SillientPay IPs
- [ ] Database backups enabled
- [ ] Error logging configured
- [ ] Payment flow tested end-to-end
- [ ] Webhook delivery verified
- [ ] Order status updates working
- [ ] Customer notifications configured
- [ ] Admin payment approval flow tested

## Monitoring

### Key Metrics to Monitor

- Webhook success rate
- Payment success rate
- Average payment time
- Failed payment reasons
- API response times
- Order status updates

### Alerts

Set up alerts for:
- Webhook failures > 5%
- API response time > 5s
- Payment success rate < 95%
- Database connection errors

## Support

**SillientPay Support:**
- Email: support@sillientpay.com
- Documentation: docs.sillientpay.com
- Status: status.sillientpay.com

**NØVRA Support:**
- Check logs in Render dashboard
- Review webhook delivery logs
- Monitor order status updates

## API Reference

### Endpoints

**Create Checkout:**
```
POST /v1/checkout
```

**Get Checkout Status:**
```
GET /v1/checkout/{checkout_id}
```

**Cancel Checkout:**
```
POST /v1/checkout/{checkout_id}/cancel
```

### Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
| 429 | Rate Limited |
| 500 | Server Error |

## Updates

### Version 1.0 (April 2026)
- Initial SillientPay integration
- Webhook signature verification
- Production & sandbox support
- Fallback to test mode
- Automatic order status updates
