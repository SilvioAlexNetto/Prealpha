import { useEffect, useState } from "react";
import "../components/Cardapio.css";
import CalendarioIcon from "../assets/icons/CalendarioIcon.png";

const BASE_URL = "https://prealpha.onrender.com";

export default function Cardapio() {
    const [dias, setDias] = useState([]);
    const [cardapio, setCardapio] = useState(() => {
        const salvo = localStorage.getItem("cardapio");
        return salvo ? JSON.parse(salvo) : {};
    });
    const [carregando, setCarregando] = useState(false);

    // 🆕 modal
    const [diaSelecionado, setDiaSelecionado] = useState(null);

    // 🆕 controla abrir/fechar preparo por refeição
    const [preparoAberto, setPreparoAberto] = useState({});

    useEffect(() => {
        gerarDiasDoMes();
    }, []);

    useEffect(() => {
        localStorage.setItem("cardapio", JSON.stringify(cardapio));
    }, [cardapio]);

    function gerarDiasDoMes() {
        const hoje = new Date();
        const ano = hoje.getFullYear();
        const mes = hoje.getMonth();
        const totalDias = new Date(ano, mes + 1, 0).getDate();

        const lista = [];
        for (let i = 1; i <= totalDias; i++) {
            lista.push(i);
        }
        setDias(lista);
    }

    async function gerarCardapio() {
        setCarregando(true);
        try {
            const res = await fetch(`${BASE_URL}/cardapio`, {
                method: "POST"
            });
            const data = await res.json();
            console.log("Retorno do cardapio", data);

            setCardapio(data.cardapio || {});

            if (data.estoque) {
                localStorage.setItem(
                    "estoque_historico",
                    JSON.stringify(data.estoque)
                );
            }
        } catch (err) {
            console.error("Erro ao gerar cardápio", err);
        }
        setCarregando(false);
    }

    const hoje = new Date();
    const mesNome = hoje.toLocaleString("pt-BR", { month: "long" });
    const ano = hoje.getFullYear();

    function togglePreparo(tipo) {
        setPreparoAberto(prev => ({
            ...prev,
            [tipo]: !prev[tipo]
        }));
    }

    return (
        <div>
            <h2 className="hp-titulo">
                <img src={CalendarioIcon} />
                Cardápio Mensal
            </h2>
            <p>{mesNome} / {ano}</p>

            <button onClick={gerarCardapio} disabled={carregando}>
                {carregando ? "Gerando..." : "Gerar Cardápio do Mês"}
            </button>

            <div className="hp-grid">
                {dias.map(dia => {
                    const dados = cardapio[dia] || {};
                    return (
                        <div
                            key={dia}
                            className="hp-card"
                            onClick={() => {
                                setDiaSelecionado({ dia, dados });
                                setPreparoAberto({});
                            }}
                        >
                            <h4>Dia {dia}</h4>

                            <p>☕ Café da manhã</p>
                            <span>{dados.cafe?.nome || "—"}</span>

                            <p>🍛 Almoço</p>
                            <span>{dados.almoco?.nome || "—"}</span>

                            <p>🌙 Jantar</p>
                            <span>{dados.jantar?.nome || "—"}</span>
                        </div>
                    );
                })}
            </div>

            {/* ===== MODAL ===== */}
            {diaSelecionado && (
                <div className="hp-overlay">
                    <div className="hp-modal">
                        <button
                            className="hp-fechar"
                            onClick={() => setDiaSelecionado(null)}
                        >
                            ✖
                        </button>

                        <h3 className="hp-titulo-h3"> <img src={CalendarioIcon} alt="" /> Dia {diaSelecionado.dia}</h3>

                        {["cafe", "almoco", "jantar"].map(tipo => {
                            const receita = diaSelecionado.dados[tipo];
                            if (!receita) return null;

                            return (
                                <div key={tipo} style={{ marginBottom: 20 }}>
                                    <h4>
                                        {tipo === "cafe" && "☕ Café da manhã"}
                                        {tipo === "almoco" && "🍛 Almoço"}
                                        {tipo === "jantar" && "🌙 Jantar"}
                                    </h4>

                                    <strong>{receita.nome}</strong>

                                    <p><b>Ingredientes:</b></p>
                                    <ul>
                                        {receita.ingredientes?.map((i, idx) => (
                                            <li key={idx}>
                                                {i.quantidade} {i.unidade} — {i.nome}
                                            </li>
                                        ))}
                                    </ul>

                                    {/* 🔽 TOGGLE */}
                                    {receita.modo_preparo && (
                                        <>
                                            <p
                                                className="hp-toggle"
                                                onClick={() => togglePreparo(tipo)}
                                            >
                                                {preparoAberto[tipo] ? "🔼 Ocultar preparo" : "🔽 Como fazer"}
                                            </p>

                                            {preparoAberto[tipo] && (
                                                <div className="hp-preparo">
                                                    <p><b>Modo de preparo:</b></p>
                                                    <ol>
                                                        {receita.modo_preparo.map((passo, idx) => (
                                                            <li key={idx}>{passo}</li>
                                                        ))}
                                                    </ol>

                                                    {receita.tempo_preparo && (
                                                        <p>
                                                            ⏱️ <b>Tempo de preparo:</b>{" "}
                                                            {receita.tempo_preparo}
                                                        </p>
                                                    )}
                                                </div>
                                            )}
                                        </>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
}