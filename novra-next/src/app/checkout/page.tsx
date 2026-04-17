'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function CheckoutPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState<'pix' | 'credit_card' | 'boleto'>('pix');
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    address: '',
    cep: ''
  });

  const handleCheckout = async () => {
    setLoading(true);
    
    try {
      // Generate order ID
      const orderId = `ORD-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      
      const response = await fetch('/api/checkout/sillientpay', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          orderId,
          amount: 499.90, // Example amount
          customerName: formData.name,
          customerEmail: formData.email,
          customerPhone: formData.phone,
          paymentMethod,
          callbackUrl: `${window.location.origin}/api/webhook/sillientpay`,
          successUrl: `${window.location.origin}/checkout/success`,
          cancelUrl: `${window.location.origin}/checkout/cancelled`
        })
      });

      const data = await response.json();

      if (data.success && data.checkoutUrl) {
        // Redirect to SillientPay checkout
        window.location.href = data.checkoutUrl;
      } else {
        alert('Erro ao criar pagamento: ' + (data.error || 'Erro desconhecido'));
        setLoading(false);
      }
    } catch (error) {
      alert('Erro ao processar checkout');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black text-white">
      {/* Header */}
      <header className="border-b border-gray-800 bg-black/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold tracking-wider">NØVRA</h1>
          <nav className="flex gap-6 text-sm">
            <a href="/" className="hover:text-gray-300 transition-colors">Home</a>
            <a href="/catalogo" className="hover:text-gray-300 transition-colors">Catálogo</a>
            <a href="/carrinho" className="hover:text-gray-300 transition-colors">Carrinho</a>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-12 max-w-4xl">
        <div className="mb-8">
          <p className="text-xs uppercase tracking-widest text-gray-500 mb-2">Checkout</p>
          <h2 className="text-4xl font-bold mb-4">Finalizar Compra</h2>
          <p className="text-gray-400">Complete seus dados para finalizar o pedido</p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Form */}
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium mb-2 text-gray-300">
                Nome Completo
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg focus:ring-2 focus:ring-white/20 focus:border-transparent outline-none transition-all"
                placeholder="Seu nome"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-gray-300">
                Email
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg focus:ring-2 focus:ring-white/20 focus:border-transparent outline-none transition-all"
                placeholder="seu@email.com"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-gray-300">
                Telefone
              </label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg focus:ring-2 focus:ring-white/20 focus:border-transparent outline-none transition-all"
                placeholder="(11) 99999-9999"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-gray-300">
                Endereço
              </label>
              <input
                type="text"
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                className="w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg focus:ring-2 focus:ring-white/20 focus:border-transparent outline-none transition-all"
                placeholder="Rua, número, complemento"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-gray-300">
                CEP
              </label>
              <input
                type="text"
                value={formData.cep}
                onChange={(e) => setFormData({ ...formData, cep: e.target.value })}
                className="w-full px-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg focus:ring-2 focus:ring-white/20 focus:border-transparent outline-none transition-all"
                placeholder="00000-000"
                required
              />
            </div>
          </div>

          {/* Payment Method */}
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium mb-4 text-gray-300">
                Método de Pagamento
              </label>
              
              <div className="space-y-3">
                <button
                  onClick={() => setPaymentMethod('pix')}
                  className={`w-full p-4 rounded-lg border-2 transition-all ${
                    paymentMethod === 'pix'
                      ? 'border-green-500 bg-green-500/10'
                      : 'border-gray-700 bg-gray-800/50 hover:border-gray-600'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-5 h-5 rounded-full border-2 flex items-center justify-center">
                      {paymentMethod === 'pix' && (
                        <div className="w-3 h-3 rounded-full bg-green-500" />
                      )}
                    </div>
                    <div className="text-left">
                      <p className="font-medium">Pix</p>
                      <p className="text-xs text-gray-400">Pagamento instantâneo</p>
                    </div>
                  </div>
                </button>

                <button
                  onClick={() => setPaymentMethod('credit_card')}
                  className={`w-full p-4 rounded-lg border-2 transition-all ${
                    paymentMethod === 'credit_card'
                      ? 'border-blue-500 bg-blue-500/10'
                      : 'border-gray-700 bg-gray-800/50 hover:border-gray-600'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-5 h-5 rounded-full border-2 flex items-center justify-center">
                      {paymentMethod === 'credit_card' && (
                        <div className="w-3 h-3 rounded-full bg-blue-500" />
                      )}
                    </div>
                    <div className="text-left">
                      <p className="font-medium">Cartão de Crédito</p>
                      <p className="text-xs text-gray-400">Até 12x sem juros</p>
                    </div>
                  </div>
                </button>

                <button
                  onClick={() => setPaymentMethod('boleto')}
                  className={`w-full p-4 rounded-lg border-2 transition-all ${
                    paymentMethod === 'boleto'
                      ? 'border-purple-500 bg-purple-500/10'
                      : 'border-gray-700 bg-gray-800/50 hover:border-gray-600'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-5 h-5 rounded-full border-2 flex items-center justify-center">
                      {paymentMethod === 'boleto' && (
                        <div className="w-3 h-3 rounded-full bg-purple-500" />
                      )}
                    </div>
                    <div className="text-left">
                      <p className="font-medium">Boleto</p>
                      <p className="text-xs text-gray-400">Vencimento em 3 dias</p>
                    </div>
                  </div>
                </button>
              </div>
            </div>

            {/* Order Summary */}
            <div className="bg-gray-800/50 rounded-lg p-6 space-y-4">
              <h3 className="font-bold text-lg">Resumo do Pedido</h3>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Subtotal</span>
                <span>R$ 499,90</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-400">Frete</span>
                <span className="text-green-400">Grátis</span>
              </div>
              <div className="border-t border-gray-700 pt-4 flex justify-between font-bold text-lg">
                <span>Total</span>
                <span>R$ 499,90</span>
              </div>
            </div>

            {/* Trust Signals */}
            <div className="flex items-center gap-4 text-xs text-gray-400">
              <div className="flex items-center gap-1">
                <span>🔒</span>
                <span>SSL 256-bit</span>
              </div>
              <div className="flex items-center gap-1">
                <span>✅</span>
                <span>Compra Segura</span>
              </div>
            </div>

            {/* Submit Button */}
            <button
              onClick={handleCheckout}
              disabled={loading}
              className="w-full py-4 bg-white text-black font-bold rounded-lg hover:bg-gray-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="w-5 h-5 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                  Processando...
                </span>
              ) : (
                'Finalizar Compra'
              )}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
