import { useEffect, useState } from "react";
import "./LoadingInicial.css";

const frases = [
    "🥗 Pequenas escolhas criam grandes mudanças.",
    "🍎 Comer bem é cuidar do seu futuro.",
    "💪 Alimentação saudável é energia para o dia.",
    "🌱 Organização na cozinha é saúde na rotina.",
    "🥑 Seu corpo reflete seus hábitos.",
    "🍽️ Planejar refeições reduz desperdício.",
    "🏃 Uma rotina saudável começa no prato."
];

export default function LoadingInicial() {
    const [fraseAtual, setFraseAtual] = useState(0);
    const [mostrarLogoInicial, setMostrarLogoInicial] = useState(true);

    // 🔥 troca frase
    useEffect(() => {
        const interval = setInterval(() => {
            setFraseAtual((prev) => (prev + 1) % frases.length);
        }, 2000);

        return () => clearInterval(interval);
    }, []);

    // 🔥 controla transição do splash fake
    useEffect(() => {
        const timer = setTimeout(() => {
            setMostrarLogoInicial(false);
        }, 700); // pode ajustar (600–900)

        return () => clearTimeout(timer);
    }, []);

    return (
        <div className="hp-loading">

            {mostrarLogoInicial ? (
                <img src="/logo.png" className="hp-splash-fake" />
            ) : (
                <>
                    <img src="/logo.png" className="hp-logo" />

                    <p className="hp-loading-frase">
                        {frases[fraseAtual]}
                    </p>
                </>
            )}

        </div>
    );
}