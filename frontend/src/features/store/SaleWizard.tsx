import { useState } from "react";
import { Card } from "@/shared/ui/Card";
import { Button } from "@/shared/ui/Button";
import { useSupplies } from "@/shared/hooks/useSupplies";
import { useCreateSale, useSaveDraft, useClearDraft } from "@/shared/hooks/useStore";
import type { SupplyData } from "@/entities/supply/types";
import { apiPost } from "@/shared/lib/api";
import { ClientStep } from "./steps/ClientStep";
import { ItemsStep } from "./steps/ItemsStep";
import { PaymentStep } from "./steps/PaymentStep";
import { ConfirmationStep } from "./steps/ConfirmationStep";
import { QrStep } from "./steps/QrStep";

interface SaleWizardProps {
  onComplete: () => void;
  onCancel: () => void;
}

interface LineItem {
  supply: SupplyData;
  quantity: number;
}

export function SaleWizard({ onComplete, onCancel }: SaleWizardProps) {
  const [step, setStep] = useState(0);
  const { data: supplies = [] } = useSupplies({ limit: 100 });
  const createSaleMutation = useCreateSale();
  const saveDraftMutation = useSaveDraft();
  const clearDraftMutation = useClearDraft();

  const [clientName, setClientName] = useState("");
  const [items, setItems] = useState<LineItem[]>([]);
  const [paymentMethod, setPaymentMethod] = useState("efectivo");
  const [qrData, setQrData] = useState<string | null>(null);
  const [notes, setNotes] = useState("");

  const [supplySearch, setSupplySearch] = useState("");
  const [selectedSupply, setSelectedSupply] = useState<SupplyData | null>(null);
  const [itemQuantity, setItemQuantity] = useState(1);

  const filteredSupplies = supplies.filter(
    (s) =>
      s.name.toLowerCase().includes(supplySearch.toLowerCase()) ||
      (s.brand && s.brand.toLowerCase().includes(supplySearch.toLowerCase()))
  );

  function addItem() {
    if (!selectedSupply) return;
    setItems([...items, { supply: selectedSupply, quantity: itemQuantity }]);
    setSelectedSupply(null);
    setItemQuantity(1);
    setSupplySearch("");
  }

  function removeItem(index: number) {
    setItems(items.filter((_, i) => i !== index));
  }

  const subtotal = items.reduce(
    (sum, item) => sum + item.quantity * Number(item.supply.unit_price),
    0
  );
  const IVA = subtotal * 0.21;
  const total = subtotal + IVA;

  async function saveDraftAndAdvance(nextStep: number) {
    await saveDraftMutation.mutateAsync({
      step,
      data: {
        client_name: clientName,
        items: items.map((i) => ({
          supply_id: i.supply.id,
          quantity: i.quantity,
          unit_price: Number(i.supply.unit_price),
        })),
        payment_method: paymentMethod,
        notes,
      },
    });
    setStep(nextStep);
  }

  async function handleConfirm() {
    try {
      const sale = await createSaleMutation.mutateAsync({
        items: items.map((i) => ({
          supply_id: i.supply.id,
          quantity: i.quantity,
          unit_price: Number(i.supply.unit_price),
        })),
        client_name: clientName || undefined,
        payment_method: paymentMethod,
        notes: notes || undefined,
      });

      if (paymentMethod !== "efectivo" && sale?.id) {
        try {
          const paymentResult = await apiPost<{ movimiento_id: string; qr_data?: string }>(
            `/pagos/venta/${sale.id}`,
            { metodo: paymentMethod, monto: total }
          );
          if (paymentResult.qr_data) {
            setQrData(paymentResult.qr_data);
            setStep(4);
            return;
          }
        } catch {
          // payment creation is optional
        }
      }

      await clearDraftMutation.mutateAsync();
      onComplete();
    } catch {
      alert("Error al crear la venta");
    }
  }

  const steps = ["Cliente", "Insumos", "Pago", "Confirmar", "QR"];
  const maxStep = qrData ? 4 : 3;

  return (
    <Card>
      <div className="flex items-center justify-center gap-2 mb-6">
        {steps.slice(0, maxStep).map((s, i) => (
          <div key={i} className="flex items-center gap-2">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                i <= step
                  ? "bg-primary-600 text-white"
                  : "bg-gray-200 text-gray-400"
              }`}
            >
              {i < step ? "✓" : i + 1}
            </div>
            <span className={`text-sm ${i <= step ? "text-gray-900 font-medium" : "text-gray-400"}`}>
              {s}
            </span>
            {i < maxStep - 1 && (
              <div
                className={`w-8 h-0.5 ${i < step ? "bg-primary-600" : "bg-gray-200"}`}
              />
            )}
          </div>
        ))}
      </div>

      {step === 0 && (
        <ClientStep
          clientName={clientName}
          onClientNameChange={setClientName}
          onCancel={onCancel}
          onNext={() => saveDraftAndAdvance(1)}
        />
      )}

      {step === 1 && (
        <ItemsStep
          supplySearch={supplySearch}
          onSupplySearchChange={(v) => { setSupplySearch(v); setSelectedSupply(null); }}
          filteredSupplies={filteredSupplies}
          selectedSupply={selectedSupply}
          onSelectSupply={(s) => { setSelectedSupply(s); setSupplySearch(s.name); }}
          itemQuantity={itemQuantity}
          onItemQuantityChange={setItemQuantity}
          onAddItem={addItem}
          items={items}
          onRemoveItem={removeItem}
          onBack={() => setStep(0)}
          onNext={() => saveDraftAndAdvance(2)}
        />
      )}

      {step === 2 && (
        <PaymentStep
          paymentMethod={paymentMethod}
          onPaymentMethodChange={setPaymentMethod}
          qrData={qrData}
          onQrDataChange={setQrData}
          notes={notes}
          onNotesChange={setNotes}
          subtotal={subtotal}
          IVA={IVA}
          total={total}
          onBack={() => setStep(1)}
          onNext={() => saveDraftAndAdvance(3)}
        />
      )}

      {step === 4 && qrData && (
        <QrStep qrData={qrData} onComplete={onComplete} />
      )}

      {step === 3 && (
        <ConfirmationStep
          clientName={clientName}
          paymentMethod={paymentMethod}
          items={items}
          subtotal={subtotal}
          IVA={IVA}
          total={total}
          notes={notes}
          loading={createSaleMutation.isPending}
          onBack={() => setStep(2)}
          onConfirm={handleConfirm}
        />
      )}
    </Card>
  );
}
