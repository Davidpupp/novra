import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';

interface SillientPayCheckoutRequest {
  orderId: string;
  amount: number;
  customerName: string;
  customerEmail: string;
  customerPhone?: string;
  paymentMethod: 'pix' | 'credit_card' | 'boleto';
  callbackUrl: string;
  successUrl: string;
  cancelUrl: string;
}

interface SillientPayResponse {
  success: boolean;
  checkoutUrl?: string;
  pixQrCode?: string;
  pixCopyPaste?: string;
  reference?: string;
  error?: string;
}

// Environment variables
const SILLIENT_PAY_ENABLED = process.env.SILLIENT_PAY_ENABLED === 'true';
const SILLIENT_PAY_API_KEY = process.env.SILLIENT_PAY_API_KEY || '';
const SILLIENT_PAY_BASE_URL = process.env.SILLIENT_PAY_BASE_URL || 'https://api.sillientpay.com';
const SILLIENT_PAY_WEBHOOK_SECRET = process.env.SILLIENT_PAY_WEBHOOK_SECRET || '';

// Log function for secure logging
function secureLog(message: string, data?: any) {
  const timestamp = new Date().toISOString();
  const logEntry = {
    timestamp,
    message,
    ...(data && { data: JSON.stringify(data) })
  };
  
  // In production, send to logging service
  console.log(JSON.stringify(logEntry));
}

// Verify webhook signature
function verifyWebhookSignature(payload: string, signature: string, secret: string): boolean {
  if (!secret) return false;
  
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');
  
  return crypto.timingSafeEqual(
    Buffer.from(expectedSignature),
    Buffer.from(signature)
  );
}

// POST /api/checkout/sillientpay - Create checkout
export async function POST(request: NextRequest) {
  try {
    const body: SillientPayCheckoutRequest = await request.json();
    
    secureLog('SillientPay checkout request received', { orderId: body.orderId, amount: body.amount });

    // Validate required fields
    if (!body.orderId || !body.amount || !body.customerName || !body.customerEmail) {
      return NextResponse.json(
        { success: false, error: 'Missing required fields' },
        { status: 400 }
      );
    }

    // If SillientPay is not enabled, return test mode
    if (!SILLIENT_PAY_ENABLED || !SILLIENT_PAY_API_KEY) {
      secureLog('SillientPay not enabled, returning test mode');
      
      return NextResponse.json<SillientPayResponse>({
        success: true,
        checkoutUrl: `/checkout/test/${body.orderId}`,
        reference: `TEST-${body.orderId}`,
        error: 'SillientPay not configured - test mode'
      });
    }

    // Create checkout via SillientPay API
    const apiUrl = `${SILLIENT_PAY_BASE_URL}/v1/checkout`;
    const headers = {
      'Authorization': `Bearer ${SILLIENT_PAY_API_KEY}`,
      'Content-Type': 'application/json'
    };

    const payload = {
      order_id: body.orderId,
      amount: body.amount,
      currency: 'BRL',
      customer: {
        name: body.customerName,
        email: body.customerEmail,
        phone: body.customerPhone
      },
      payment_method: body.paymentMethod,
      callback_url: body.callbackUrl,
      success_url: body.successUrl,
      cancel_url: body.cancelUrl,
      metadata: {
        timestamp: new Date().toISOString(),
        source: 'novra-nextjs'
      }
    };

    secureLog('Calling SillientPay API', { url: apiUrl, payload: { ...payload, customer: '***' } });

    const response = await fetch(apiUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errorText = await response.text();
      secureLog('SillientPay API error', { status: response.status, error: errorText });
      
      throw new Error(`SillientPay API error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    
    secureLog('SillientPay checkout created successfully', { 
      reference: data.reference,
      checkoutUrl: data.checkout_url ? '***' : 'none'
    });

    return NextResponse.json<SillientPayResponse>({
      success: true,
      checkoutUrl: data.checkout_url,
      pixQrCode: data.pix_qr_code,
      pixCopyPaste: data.pix_copy_paste,
      reference: data.reference
    });

  } catch (error) {
    secureLog('SillientPay checkout error', { 
      error: error instanceof Error ? error.message : 'Unknown error'
    });
    
    return NextResponse.json<SillientPayResponse>({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to create checkout'
    }, { status: 500 });
  }
}

// GET /api/checkout/sillientpay - Get checkout status
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const checkoutId = searchParams.get('checkoutId');

    if (!checkoutId) {
      return NextResponse.json(
        { success: false, error: 'Missing checkoutId' },
        { status: 400 }
      );
    }

    if (!SILLIENT_PAY_ENABLED || !SILLIENT_PAY_API_KEY) {
      return NextResponse.json({
        success: true,
        status: 'test',
        checkoutId
      });
    }

    const apiUrl = `${SILLIENT_PAY_BASE_URL}/v1/checkout/${checkoutId}`;
    const headers = {
      'Authorization': `Bearer ${SILLIENT_PAY_API_KEY}`,
      'Content-Type': 'application/json'
    };

    const response = await fetch(apiUrl, {
      method: 'GET',
      headers
    });

    if (!response.ok) {
      throw new Error(`SillientPay API error: ${response.status}`);
    }

    const data = await response.json();

    return NextResponse.json({
      success: true,
      status: data.status,
      paidAt: data.paid_at
    });

  } catch (error) {
    secureLog('SillientPay status check error', { 
      error: error instanceof Error ? error.message : 'Unknown error'
    });
    
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Failed to check status'
    }, { status: 500 });
  }
}
