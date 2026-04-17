import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';

interface WebhookPayload {
  reference: string;
  status: string;
  amount: number;
  payment_method: string;
  paid_at?: string;
  metadata?: {
    order_id: string;
    timestamp: string;
    source: string;
  };
}

// Environment variables
const SILLIENT_PAY_WEBHOOK_SECRET = process.env.SILLIENT_PAY_WEBHOOK_SECRET || '';

// Log function for secure logging
function secureLog(message: string, data?: any) {
  const timestamp = new Date().toISOString();
  const logEntry = {
    timestamp,
    message,
    ...(data && { data: JSON.stringify(data) })
  };
  
  console.log(JSON.stringify(logEntry));
}

// Verify webhook signature
function verifyWebhookSignature(payload: string, signature: string, secret: string): boolean {
  if (!secret) {
    secureLog('Webhook secret not configured, skipping verification');
    return true; // Allow if secret not configured (dev mode)
  }
  
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');
  
  return crypto.timingSafeEqual(
    Buffer.from(expectedSignature),
    Buffer.from(signature)
  );
}

// POST /api/webhook/sillientpay - Handle SillientPay webhook
export async function POST(request: NextRequest) {
  try {
    const signature = request.headers.get('x-sillient-signature') || '';
    const payload = await request.text();
    
    secureLog('SillientPay webhook received', { 
      signature: signature ? 'present' : 'missing',
      payloadLength: payload.length
    });

    // Verify webhook signature
    if (!verifyWebhookSignature(payload, signature, SILLIENT_PAY_WEBHOOK_SECRET)) {
      secureLog('Invalid webhook signature', { signature });
      return NextResponse.json(
        { success: false, error: 'Invalid signature' },
        { status: 401 }
      );
    }

    // Parse webhook payload
    const webhookData: WebhookPayload = JSON.parse(payload);
    
    secureLog('Webhook payload parsed', { 
      reference: webhookData.reference,
      status: webhookData.status 
    });

    // Validate required fields
    if (!webhookData.reference || !webhookData.status) {
      return NextResponse.json(
        { success: false, error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // Map SillientPay status to internal status
    const statusMapping: Record<string, string> = {
      'approved': 'paid',
      'paid': 'paid',
      'confirmed': 'paid',
      'pending': 'awaiting_payment',
      'cancelled': 'cancelled',
      'failed': 'failed',
      'refunded': 'refunded'
    };

    const internalStatus = statusMapping[webhookData.status] || webhookData.status;

    // TODO: Update order in database
    // This would typically update a database record
    // For now, we'll log the update
    secureLog('Order status update', {
      reference: webhookData.reference,
      newStatus: internalStatus,
      paymentMethod: webhookData.payment_method,
      paidAt: webhookData.paid_at
    });

    // Here you would typically:
    // 1. Find order by reference
    // 2. Update order status
    // 3. Send confirmation email to customer
    // 4. Update inventory
    // 5. Trigger fulfillment

    return NextResponse.json({ success: true });

  } catch (error) {
    secureLog('Webhook processing error', { 
      error: error instanceof Error ? error.message : 'Unknown error'
    });
    
    return NextResponse.json(
      { success: false, error: 'Failed to process webhook' },
      { status: 500 }
    );
  }
}

// GET /api/webhook/sillientpay - Health check
export async function GET() {
  return NextResponse.json({
    success: true,
    status: 'active',
    webhookSecret: SILLIENT_PAY_WEBHOOK_SECRET ? 'configured' : 'not configured'
  });
}
