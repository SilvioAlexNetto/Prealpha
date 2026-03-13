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

    useEffect(() => {
        const interval = setInterval(() => {
            setFraseAtual((prev) => (prev + 1) % frases.length);
        }, 2000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="hp-loading">
            <h1 className="hp-loading-logo">Health Pantry</h1>

            <div className="hp-spinner"></div>

            <p className="hp-loading-frase">
                {frases[fraseAtual]}
            </p>
        </div>
    );
}