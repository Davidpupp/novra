'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';

function CheckoutPendingContent() {
  const searchParams = useSearchParams();
  const [orderId, setOrderId] = useState<string | null>(null);
  const [countdown, setCountdown] = useState(300); // 5 minutes in seconds

  useEffect(() => {
    const orderIdParam = searchParams.get('orderId');
    if (orderIdParam) {
      setOrderId(orderIdParam);
    }

    // Countdown timer
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [searchParams]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black text-white flex items-center justify-center px-6">
      <div className="max-w-lg w-full text-center">
        {/* Pending Icon */}
        <div className="w-24 h-24 bg-yellow-500 rounded-full flex items-center justify-center mx-auto mb-8 animate-pulse">
          <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>

        {/* Heading */}
        <h1 className="text-4xl font-bold mb-4">Pagamento Pendente</h1>
        <p className="text-gray-400 mb-8">
          {orderId ? `Pedido #${orderId} aguardando pagamento.` : 'Seu pedido está aguardando pagamento.'}
        </p>

        {/* Countdown */}
        <div className="bg-gray-800/50 rounded-lg p-6 mb-8">
          <p className="text-sm text-gray-400 mb-2">Tempo restante para pagamento</p>
          <p className="text-5xl font-bold text-yellow-400">{formatTime(countdown)}</p>
          <p className="text-xs text-gray-500 mt-2">Após este prazo, o pedido será cancelado</p>
        </div>

        {/* Payment Methods */}
        <div className="bg-gray-800/50 rounded-lg p-6 mb-8 text-left">
          <h2 className="font-bold text-lg mb-4">Formas de Pagamento</h2>
          <div className="space-y-3 text-sm">
            <div className="flex items-center gap-3 p-3 bg-gray-700/50 rounded-lg">
              <span className="text-2xl">💠</span>
              <div>
                <p className="font-medium">Pix</p>
                <p className="text-xs text-gray-400">Pagamento instantâneo via QR Code</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-gray-700/50 rounded-lg">
              <span className="text-2xl">💳</span>
              <div>
                <p className="font-medium">Cartão de Crédito</p>
                <p className="text-xs text-gray-400">Até 12x sem juros</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-gray-700/50 rounded-lg">
              <span className="text-2xl">📄</span>
              <div>
                <p className="font-medium">Boleto</p>
                <p className="text-xs text-gray-400">Vencimento em 3 dias úteis</p>
              </div>
            </div>
          </div>
        </div>

        {/* Instructions */}
        <div className="bg-gray-800/50 rounded-lg p-6 mb-8 text-left">
          <h2 className="font-bold text-lg mb-4">Instruções</h2>
          <ol className="space-y-3 text-sm text-gray-300 list-decimal list-inside">
            <li>Escolha a forma de pagamento</li>
            <li>Siga as instruções na tela de pagamento</li>
            <li>Aguarde a confirmação (pode levar até 30 minutos)</li>
            <li>Você receberá um email com a confirmação</li>
          </ol>
        </div>

        {/* Actions */}
        <div className="space-y-4">
          <button
            onClick={() => window.location.reload()}
            className="block w-full py-4 bg-white text-black font-bold rounded-lg hover:bg-gray-200 transition-all"
          >
            Verificar Status do Pagamento
          </button>
          <a
            href="/carrinho"
            className="block w-full py-4 bg-gray-800 text-white font-bold rounded-lg hover:bg-gray-700 transition-all text-center"
          >
            Voltar ao Carrinho
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

export default function CheckoutPendingPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black text-white flex items-center justify-center px-6">
      <div className="text-center">Carregando...</div>
    </div>}>
      <CheckoutPendingContent />
    </Suspense>
  );
}
