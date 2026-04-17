import { NextRequest, NextResponse } from "next/server";
import { Preference } from "mercadopago";
import { mercadoPago } from "@/lib/mercadopago";

export async function POST(req: NextRequest) {
  const body = await req.json();
  const { items } = body as { items: Array<{ name: string; price: number; quantity: number }> };

  const preference = await new Preference(mercadoPago).create({
    body: {
      items: items.map((item) => ({
        title: item.name,
        quantity: item.quantity,
        unit_price: item.price,
        currency_id: "BRL"
      })),
      back_urls: {
        success: `${process.env.NEXT_PUBLIC_APP_URL}/sucesso`,
        failure: `${process.env.NEXT_PUBLIC_APP_URL}/checkout`
      },
      auto_return: "approved"
    }
  });

  return NextResponse.json({ checkoutUrl: preference.init_point });
}
