import { useEffect, useState } from "react";
import "../components/Cardapio.css";
import CalendarioTwoIcon from "../assets/icons/CalendarioTwoIcon.png";
import CafeIcon from "../assets/icons/CafeIcon.png";
import JantarIcon from "../assets/icons/JantarIcon.png";
import AlmocoIcon from "../assets/icons/AlmocoIcon.png";

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
            const hoje = new Date();

            const body = {
                mes: hoje.getMonth() + 1,
                ano: hoje.getFullYear()
            };

            const res = await fetch(`${BASE_URL}/cardapio/gerar`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(body)
            });

            const data = await res.json();

            console.log("STATUS:", data.status);
            console.log("CARDAPIO:", data.cardapio);
            console.log("FULL DATA:", data);

            setCardapio(data.cardapio || {});
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
            <h2 className="hp-titulo"> <img src={CalendarioTwoIcon} /> Cardápio Mensal </h2>
            <p>{mesNome} / {ano}</p>

            <button
                className="hp-btn-gerar"
                onClick={gerarCardapio}
                disabled={carregando}
            >
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

                            {/* CAFÉ */}
                            <p className="hp-refeicao">
                                <img src={CafeIcon} alt="Café" className="hp-icon" />
                                Café da manhã
                            </p>
                            <span>{dados.cafe?.nome || "—"}</span>

                            {/* ALMOÇO */}
                            <p className="hp-refeicao">
                                <img src={AlmocoIcon} alt="Almoço" className="hp-icon" />
                                Almoço
                            </p>
                            <span>{dados.almoco?.nome || "—"}</span>

                            {/* JANTAR */}
                            <p className="hp-refeicao">
                                <img src={JantarIcon} alt="Jantar" className="hp-icon" />
                                Jantar
                            </p>
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

                        <h3 className="hp-titulo-h3"> <img src={CalendarioTwoIcon} alt="" /> Dia {diaSelecionado.dia}</h3>

                        {["cafe", "almoco", "jantar"].map(tipo => {
                            const receita = diaSelecionado.dados[tipo];
                            if (!receita) return null;

                            return (
                                <div key={tipo} style={{ marginBottom: 20 }}>
                                    <h4>
                                        {tipo === "cafe" && (<><img src={CafeIcon} alt="Café da manhã" className="hp-icon" /> Café da manhã </>)}
                                        {tipo === "almoco" && (<><img src={AlmocoIcon} alt="Almoço" className="hp-icon" /> Almoço </>)}
                                        {tipo === "jantar" && (<><img src={JantarIcon} alt="Jantar" className="hp-icon" /> Jantar </>)}
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