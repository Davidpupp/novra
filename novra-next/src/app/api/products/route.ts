import { NextResponse } from "next/server";

const mockProducts = [
  { id: "nv-001", name: "Oversized Tee Shadow", category: "streetwear", price: 289 },
  { id: "nv-002", name: "Cargo Pant Concrete", category: "streetwear", price: 499 },
  { id: "nv-003", name: "Tech Jacket Noir", category: "premium", price: 899 }
];

export async function GET() {
  return NextResponse.json({ items: mockProducts });
}
