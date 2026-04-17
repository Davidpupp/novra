'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';

function CheckoutSuccessContent() {
  const searchParams = useSearchParams();
  const [orderId, setOrderId] = useState<string | null>(null);

  useEffect(() => {
    const orderIdParam = searchParams.get('orderId');
    if (orderIdParam) {
      setOrderId(orderIdParam);
    }
  }, [searchParams]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black text-white flex items-center justify-center px-6">
      <div className="max-w-lg w-full text-center">
        {/* Success Icon */}
        <div className="w-24 h-24 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-8">
          <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
          </svg>
        </div>

        {/* Heading */}
        <h1 className="text-4xl font-bold mb-4">Pagamento Aprovado!</h1>
        <p className="text-gray-400 mb-8">
          {orderId ? `Pedido #${orderId} confirmado com sucesso.` : 'Seu pedido foi confirmado com sucesso.'}
        </p>

        {/* Order Details */}
        <div className="bg-gray-800/50 rounded-lg p-6 mb-8 text-left">
          <h2 className="font-bold text-lg mb-4">Detalhes do Pedido</h2>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Status</span>
              <span className="text-green-400 font-medium">Pago</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Data</span>
              <span>{new Date().toLocaleDateString('pt-BR')}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Forma de Pagamento</span>
              <span>Pix</span>
            </div>
          </div>
        </div>

        {/* Next Steps */}
        <div className="bg-gray-800/50 rounded-lg p-6 mb-8 text-left">
          <h2 className="font-bold text-lg mb-4">Próximos Passos</h2>
          <ul className="space-y-3 text-sm text-gray-300">
            <li className="flex items-start gap-2">
              <span className="text-green-400 mt-1">✓</span>
              <span>Confirmação enviada para seu email</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-green-400 mt-1">✓</span>
              <span>Preparação do pedido iniciada</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-gray-500 mt-1">○</span>
              <span>Envio em 1-2 dias úteis</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-gray-500 mt-1">○</span>
              <span>Rastreamento por email</span>
            </li>
          </ul>
        </div>

        {/* Actions */}
        <div className="space-y-4">
          <a
            href="/"
            className="block w-full py-4 bg-white text-black font-bold rounded-lg hover:bg-gray-200 transition-all text-center"
          >
            Continuar Comprando
          </a>
          <a
            href="/conta/pedidos"
            className="block w-full py-4 bg-gray-800 text-white font-bold rounded-lg hover:bg-gray-700 transition-all text-center"
          >
            Ver Meus Pedidos
          </a>
        </div>

        {/* Support */}
        <p className="text-xs text-gray-500 mt-8">
          Precisa de ajuda? Entre em contato: <a href="mailto:suporte@novra.com" className="underline hover:text-white">suporte@novra.com</a>
        </p>
      </div>
    </div>
  );
}

export default function CheckoutSuccessPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black text-white flex items-center justify-center px-6">
      <div className="text-center">Carregando...</div>
    </div>}>
      <CheckoutSuccessContent />
    </Suspense>
  );
}
