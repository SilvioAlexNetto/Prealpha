import { useState } from "react";

export default function Loja() {
    const [isPremium, setIsPremium] = useState(
        localStorage.getItem("isPremium") === "true"
    );

    function ativarPremium() {
        localStorage.setItem("isPremium", "true");
        setIsPremium(true);
    }

    return (
        <div style={container}>
            <h2>🛒 Loja</h2>

            <div style={card}>
                <h3>🌟 Conta Premium</h3>

                <ul style={lista}>
                    <li>✅ App sem anúncios</li>
                    <li>✅ Acesso à ficha nutricional</li>
                    <li>✅ Cálculos avançados de saúde</li>
                </ul>

                {isPremium ? (
                    <div style={ativo}>
                        🎉 Premium ativo
                    </div>
                ) : (
                    <button style={botao} onClick={ativarPremium}>
                        Ativar Premium
                    </button>
                )}
            </div>
        </div>
    );
}

/* =========================
   ESTILOS
========================= */

const container = {
    padding: 20,
};

const card = {
    background: "#FAFAFA",
    borderRadius: 12,
    padding: 20,
    maxWidth: 400,
    margin: "0 auto",
    boxShadow: "0 4px 10px rgba(0,0,0,0.05)",
};

const lista = {
    listStyle: "none",
    padding: 0,
    marginBottom: 20,
};

const botao = {
    width: "100%",
    padding: 12,
    background: "#4CAF50",
    color: "#fff",
    border: "none",
    borderRadius: 8,
    fontSize: 16,
    cursor: "pointer",
};

const ativo = {
    textAlign: "center",
    padding: 12,
    background: "#E8F5E9",
    color: "#2E7D32",
    borderRadius: 8,
    fontWeight: "bold",
};