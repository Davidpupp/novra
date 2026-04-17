import { NextRequest, NextResponse } from "next/server";
import { stripe } from "@/lib/stripe";

export async function POST(req: NextRequest) {
  const body = await req.json();
  const { items } = body as { items: Array<{ name: string; price: number; quantity: number }> };

  const session = await stripe.checkout.sessions.create({
    mode: "payment",
    line_items: items.map((item) => ({
      quantity: item.quantity,
      price_data: {
        currency: "brl",
        product_data: { name: item.name },
        unit_amount: Math.round(item.price * 100)
      }
    })),
    success_url: `${process.env.NEXT_PUBLIC_APP_URL}/sucesso`,
    cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/checkout`
  });

  return NextResponse.json({ checkoutUrl: session.url });
}
