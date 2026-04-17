import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';
import { createClient } from '@supabase/supabase-js';

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
const SUPABASE_URL = process.env.SUPABASE_URL || '';
const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY || '';

// Initialize Supabase client
const supabase = SUPABASE_URL && SUPABASE_ANON_KEY 
  ? createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
  : null;

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

    // Update order in database
    if (supabase) {
      try {
        const { error } = await supabase
          .from('orders')
          .update({
            status: internalStatus,
            paid_at: webhookData.paid_at,
            payment_method: webhookData.payment_method,
            updated_at: new Date().toISOString()
          })
          .eq('payment_reference', webhookData.reference);

        if (error) {
          secureLog('Database update failed', { error: error.message });
          // Don't fail the webhook response for DB errors
          // Log and continue to ensure webhook is acknowledged
        } else {
          secureLog('Order status updated in database', {
            reference: webhookData.reference,
            newStatus: internalStatus
          });
        }
      } catch (dbError) {
        secureLog('Database error', { 
          error: dbError instanceof Error ? dbError.message : 'Unknown DB error'
        });
        // Don't fail webhook response for DB errors
      }
    } else {
      secureLog('Supabase not configured, skipping database update');
    }

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
