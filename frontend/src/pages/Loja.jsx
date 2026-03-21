import { useState } from "react";
import "../components/Loja.css";
import LojaIcon from "../assets/icons/LojaIcon.png";

export default function Loja() {
    const [isPremium, setIsPremium] = useState(
        localStorage.getItem("isPremium") === "true"
    );

    function ativarPremium() {
        localStorage.setItem("isPremium", "true");
        setIsPremium(true);
    }

    return (
        <div className="hp-loja-container">
            <h2 className="hp-titulo"> <img src={LojaIcon} /> Loja </h2>

            <div className="hp-loja-card">
                <h3>🌟 Conta Premium</h3>

                <ul className="hp-loja-lista">
                    <li>✅ App sem anúncios</li>
                    <li>✅ Acesso à ficha nutricional</li>
                    <li>✅ Cálculos avançados de saúde</li>
                </ul>

                {isPremium ? (
                    <div className="hp-loja-ativo">
                        🎉 Premium ativo
                    </div>
                ) : (
                    <button className="hp-btn" onClick={ativarPremium}>
                        Ativar Premium
                    </button>
                )}
            </div>
        </div>
    );
}