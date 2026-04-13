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

    // 🆕 PROGRESSO
    const [progresso, setProgresso] = useState(() => {
        try {
            return JSON.parse(localStorage.getItem("progresso")) || {};
        } catch {
            return {};
        }
    });

    const [carregando, setCarregando] = useState(false);
    const [diaSelecionado, setDiaSelecionado] = useState(null);
    const [preparoAberto, setPreparoAberto] = useState({});

    // 🆕 ANIMAÇÃO
    const [animacaoDia, setAnimacaoDia] = useState(null);

    useEffect(() => {
        gerarDiasDoMes();
    }, []);

    // 🆕 RESET AUTOMÁTICO POR MÊS
    useEffect(() => {
        const hoje = new Date();
        const prefixoMes = `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, "0")}`;

        const progressoFiltrado = Object.fromEntries(
            Object.entries(progresso).filter(([key]) => key.startsWith(prefixoMes))
        );

        // só atualiza se realmente mudou (evita loop infinito)
        if (JSON.stringify(progressoFiltrado) !== JSON.stringify(progresso)) {
            setProgresso(progressoFiltrado);
        }

    }, []); // roda só ao carregar o componente

    useEffect(() => {
        localStorage.setItem("cardapio", JSON.stringify(cardapio));
    }, [cardapio]);

    // 🆕 salvar progresso
    useEffect(() => {
        localStorage.setItem("progresso", JSON.stringify(progresso));
    }, [progresso]);

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
            const estoque = JSON.parse(localStorage.getItem("estoque") || "[]");

            setCardapio({});

            await fetch(`${BASE_URL}/estoque`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(estoque)
            });

            const custom = JSON.parse(localStorage.getItem("ingredientes_custom") || "{}");

            const res = await fetch(`${BASE_URL}/cardapio`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    ingredientes_custom: custom
                })
            });
            console.log("CUSTOM ENVIADO:", custom);

            if (!res.ok) throw new Error("Erro ao gerar cardápio");

            const data = await res.json();
            console.log("Retorno do cardapio", data);

            setCardapio(data.cardapio || {});

            if (data.estoque) {
                localStorage.setItem(
                    "estoque_historico",
                    JSON.stringify({
                        sobras: data.sobras || [],
                        consumidos: data.consumidos || []
                    })
                );
            }

        } catch (err) {
            console.error("Erro ao gerar cardápio", err);
            alert("Erro ao gerar cardápio");
        }

        setCarregando(false);
    }

    const hoje = new Date();
    const mesNome = hoje.toLocaleString("pt-BR", { month: "long" });
    const ano = hoje.getFullYear();
    const diaHoje = hoje.getDate();
    const mesAtual = hoje.getMonth();
    const anoAtual = hoje.getFullYear();

    function getStatusDia(dia) {
        if (dia < diaHoje) return "passado";
        if (dia === diaHoje) return "hoje";
        return "futuro";
    }

    function getDataKey(date) {
        return date.toISOString().split("T")[0];
    }

    const dataSelecionada = diaSelecionado
        ? new Date(anoAtual, mesAtual, diaSelecionado.dia)
        : null;

    const keySelecionado = dataSelecionada
        ? getDataKey(dataSelecionada)
        : null;

    function togglePreparo(tipo) {
        setPreparoAberto(prev => ({
            ...prev,
            [tipo]: !prev[tipo]
        }));
    }

    // 🆕 função central de animação
    function triggerAnimacao(dia) {
        setAnimacaoDia(dia);
        setTimeout(() => setAnimacaoDia(null), 1500);
    }

    // 🆕 marcar refeição
    function toggleRefeicao(dia, tipo) {
        const data = new Date(anoAtual, mesAtual, dia);
        const key = getDataKey(data);

        setProgresso(prev => {
            const novo = {
                ...prev,
                [key]: {
                    ...prev[key],
                    [tipo]: !prev[key]?.[tipo]
                }
            };

            const d = novo[key];

            if (d?.cafe && d?.almoco && d?.jantar) {
                triggerAnimacao(dia);
            }

            return novo;
        });

        window.dispatchEvent(new Event("streakAtualizado"));
    }

    // 🆕 concluir dia inteiro
    function concluirDia(dia) {
        const data = new Date(anoAtual, mesAtual, dia);
        const key = getDataKey(data);

        setProgresso(prev => ({
            ...prev,
            [key]: {
                cafe: true,
                almoco: true,
                jantar: true
            }
        }));

        triggerAnimacao(dia);
        window.dispatchEvent(new Event("streakAtualizado"));
    }

    const statusSelecionado = diaSelecionado
        ? getStatusDia(diaSelecionado.dia)
        : null;

    const podeMarcar = statusSelecionado === "hoje";

    return (
        <>
            <div>
                <h2 className="hp-titulo">
                    <img src={CalendarioTwoIcon} /> Cardápio Mensal
                </h2>
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

                        const status = getStatusDia(dia);

                        const bloqueado = false;
                        const futuro = status === "futuro";

                        const dados = cardapio[dia] || {};
                        const data = new Date(anoAtual, mesAtual, dia);
                        const key = getDataKey(data);
                        const progressoDia = progresso[key] || {};

                        const completo =
                            progressoDia.cafe &&
                            progressoDia.almoco &&
                            progressoDia.jantar;


                        return (
                            <div
                                key={dia}
                                className={`hp-card 
                                    ${completo ? "completo" : ""} 
                                    ${animacaoDia === dia ? "animando" : ""}
                                    ${bloqueado ? "bloqueado" : ""}
                                    ${futuro ? "futuro" : ""}
                                `}
                                onClick={() => {
                                    if (bloqueado) return;
                                    setDiaSelecionado({ dia, dados });
                                    setPreparoAberto({});
                                }}

                            >

                                <h4>Dia {dia}</h4>

                                {/* 🆕 PROGRESSO VISUAL */}
                                <p>
                                    {progressoDia.cafe ? "☕✅" : "☕⬜"}
                                    {progressoDia.almoco ? " 🍛✅" : " 🍛⬜"}
                                    {progressoDia.jantar ? " 🍽️✅" : " 🍽️⬜"}
                                </p>

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

                            <h3 className="hp-titulo-h3">
                                <img src={CalendarioTwoIcon} /> Dia {diaSelecionado.dia}
                            </h3>

                            <div className="hp-modal-content">


                                {/* 🆕 BOTÃO CONCLUIR DIA */}
                                <button
                                    onClick={() => concluirDia(diaSelecionado.dia)}

                                    disabled={!podeMarcar}
                                    style={{ marginBottom: 15 }}
                                >
                                    ✅ Concluir dia
                                </button>

                                {["cafe", "almoco", "jantar"].map(tipo => {
                                    const receita = diaSelecionado.dados[tipo];
                                    const status = getStatusDia(diaSelecionado.dia);
                                    const podeMarcar = status === "hoje";
                                    if (!receita) return null;

                                    return (
                                        <div key={tipo} style={{ marginBottom: 20 }}>
                                            <h4>
                                                {tipo === "cafe" && (<><img src={CafeIcon} className="hp-icon" /> Café da manhã </>)}
                                                {tipo === "almoco" && (<><img src={AlmocoIcon} className="hp-icon" /> Almoço </>)}
                                                {tipo === "jantar" && (<><img src={JantarIcon} className="hp-icon" /> Jantar </>)}
                                            </h4>

                                            {/* 🆕 CHECKBOX */}

                                            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>

                                                <input
                                                    type="checkbox"
                                                    disabled={!podeMarcar}
                                                    checked={keySelecionado ? progresso[keySelecionado]?.[tipo] || false : false}
                                                    onChange={() => toggleRefeicao(diaSelecionado.dia, tipo)}
                                                />
                                                <strong>{receita.nome}</strong>
                                            </div>

                                            <p><b>Ingredientes:</b></p>
                                            <ul>
                                                {receita.ingredientes?.map((i, idx) => (
                                                    <li key={idx}>
                                                        {i.quantidade} {i.unidade} — {i.nome}
                                                    </li>
                                                ))}
                                            </ul>

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
                                                            <ol>
                                                                {receita.modo_preparo.map((passo, idx) => (
                                                                    <li key={idx}>{passo}</li>
                                                                ))}
                                                            </ol>
                                                        </div>
                                                    )}
                                                </>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* 🎊 CONFETE GLOBAL */}
            {animacaoDia && (
                <div className="confete-container">
                    {Array.from({ length: 20 }).map((_, i) => (
                        <span
                            key={i}
                            className="confete"
                            style={{ left: `${Math.random() * 100}%` }}
                        />
                    ))}
                </div>
            )}
        </>
    );
}