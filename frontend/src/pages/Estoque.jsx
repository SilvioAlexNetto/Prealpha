import { useState, useEffect, useRef } from "react";
import Quagga from "quagga";

export default function Estoque() {
    const [nomeDigitado, setNomeDigitado] = useState("");
    const [ingredienteSelecionado, setIngredienteSelecionado] = useState(null);

    const [quantidade, setQuantidade] = useState("");
    const [unidade, setUnidade] = useState("");
    const [numeroPacotes, setNumeroPacotes] = useState("");

    const [modoHistorico, setModoHistorico] = useState(false);

    const [estoque, setEstoque] = useState(() => {
        const salvo = localStorage.getItem("estoque");
        return salvo ? JSON.parse(salvo) : [];
    });

    const [historico, setHistorico] = useState(() => {
        const salvo = localStorage.getItem("estoque_historico");
        return salvo ? JSON.parse(salvo) : [];
    });

    const [ingredientesBanco, setIngredientesBanco] = useState([]);
    const [unidadesBanco, setUnidadesBanco] = useState([]);

    const [cameraAtiva, setCameraAtiva] = useState(false);
    const [tempoRestante, setTempoRestante] = useState(10);
    const [produtoEscaneado, setProdutoEscaneado] = useState(null);

    const timerRef = useRef(null);
    const quaggaAtivoRef = useRef(false);

    useEffect(() => {
        fetch("${BASE_URL}/ingredientes")
            .then(res => res.json())
            .then(data => {
                setIngredientesBanco(data.ingredientes || []);
                setUnidadesBanco(data.unidades || []);
            })
            .catch(() => {
                setIngredientesBanco([]);
                setUnidadesBanco([]);
            });
    }, []);

    useEffect(() => {
        localStorage.setItem("estoque", JSON.stringify(estoque));
    }, [estoque]);

    function adicionarItem() {
        if (!ingredienteSelecionado || !quantidade || !unidade) return;

        // 🔴 VALIDAÇÃO OBRIGATÓRIA
        if (!numeroPacotes || Number(numeroPacotes) < 1) {
            alert("Informe o N° de pacotes (mínimo 1).");
            return;
        }

        const quantidadeFinal = Number(quantidade) * Number(numeroPacotes);

        const novoEstoque = [
            ...estoque,
            {
                nome: ingredienteSelecionado.nome,
                quantidade: quantidadeFinal,
                unidade
            }
        ];

        setEstoque(novoEstoque);
        enviarEstoqueParaAPI(novoEstoque);

        setNomeDigitado("");
        setIngredienteSelecionado(null);
        setQuantidade("");
        setUnidade("");
        setNumeroPacotes(1);
    }

    function removerItem(index) {
        const novoEstoque = estoque.filter((_, i) => i !== index);
        setEstoque(novoEstoque);
        enviarEstoqueParaAPI(novoEstoque);
    }

    function limparEstoque() {
        if (!confirm("Deseja limpar todo o estoque?")) return;
        setEstoque([]);
        localStorage.removeItem("estoque");
        enviarEstoqueParaAPI([]);
    }

    function limparHistorico() {
        if (!confirm("Deseja limpar o histórico?")) return;
        setHistorico([]);
        localStorage.removeItem("estoque_historico");
    }

    function enviarEstoqueParaAPI(novoEstoque) {
        fetch("${BASE_URL}/estoque", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(novoEstoque),
        });
    }

    const sugestoes = ingredientesBanco.filter(nome =>
        nome.toLowerCase().includes(nomeDigitado.toLowerCase())
    );

    // ============================
    // 🔥 NOVOS STATES (ADICIONE JUNTO AOS OUTROS STATES DO COMPONENTE)
    // ============================

    const [mostrarAvisoIngrediente, setMostrarAvisoIngrediente] = useState(false);
    const [sugestoesIngredientes, setSugestoesIngredientes] = useState([]);

    // ============================
    // 🔥 FUNÇÃO PARA AUTOCOMPLETE IGUAL AO MANUAL
    // ============================

    function handleEditarNomeProduto(valor) {
        const nomeEditado = valor;

        setProdutoEscaneado(prev => ({
            ...prev,
            nome: nomeEditado
        }));

        if (typeof ingredientesBanco !== "undefined" && Array.isArray(ingredientesBanco)) {
            const filtrados = ingredientesBanco.filter(item =>
                item.toLowerCase().includes(nomeEditado.toLowerCase())
            ).slice(0, 5);

            setSugestoesIngredientes(filtrados);
        }
    }

    // ============================
    // 🔥 FUNÇÃO PARA SELECIONAR SUGESTÃO
    // ============================

    function selecionarSugestao(nome) {
        setProdutoEscaneado(prev => ({
            ...prev,
            nome
        }));
        setSugestoesIngredientes([]);
    }

    // ============================
    // 🔥 SUA FUNÇÃO ORIGINAL (NÃO REMOVIDO NADA)
    // ============================

    async function iniciarLeituraCodigo() {
        if (quaggaAtivoRef.current) return;

        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            const cameras = devices.filter(d => d.kind === "videoinput");

            if (cameras.length === 0) {
                alert("Nenhuma câmera encontrada.");
                return;
            }

            const cameraPreferida =
                cameras.find(c => /iriun|webion|virtual/i.test(c.label)) || cameras[0];

            setCameraAtiva(true);
            setTempoRestante(10);
            quaggaAtivoRef.current = true;

            requestAnimationFrame(() => {
                const target = document.querySelector("#camera");

                if (!target) {
                    alert("Erro ao acessar elemento da câmera.");
                    encerrarCamera();
                    return;
                }

                Quagga.init(
                    {
                        inputStream: {
                            type: "LiveStream",
                            target,
                            constraints: {
                                deviceId: cameraPreferida.deviceId,
                                facingMode: "environment"
                            }
                        },
                        locator: { patchSize: "medium", halfSample: true },
                        numOfWorkers: navigator.hardwareConcurrency || 4,
                        frequency: 10,
                        decoder: { readers: ["ean_reader"] },
                        locate: true
                    },
                    err => {
                        if (err) {
                            console.error(err);
                            alert("Erro ao iniciar a câmera.");
                            encerrarCamera();
                            return;
                        }
                        Quagga.start();
                    }
                );

                let codigoDetectado = null;

                Quagga.onDetected(async data => {
                    const codigo = data.codeResult.code.replace(/\D/g, "").trim();

                    if (codigo.length !== 13) return;
                    if (codigoDetectado === codigo) return;

                    codigoDetectado = codigo;
                    encerrarCamera();

                    try {
                        const res = await fetch(
                            `https://world.openfoodfacts.org/api/v0/product/${codigo}.json`
                        );
                        const json = await res.json();

                        if (json.status !== 1) {
                            alert("Produto não encontrado. Cadastre manualmente.");
                            return;
                        }

                        const produto = json.product;

                        const normalizar = texto =>
                            texto?.toLowerCase()
                                .normalize("NFD")
                                .replace(/[\u0300-\u036f]/g, "")
                                .replace(/[^\w\s]/g, "")
                                .trim() || "";

                        const capitalizar = texto =>
                            texto.replace(/\b\w/g, l => l.toUpperCase());

                        let nomeBase = produto.product_name || "";
                        nomeBase = nomeBase.split(" - ")[0];
                        nomeBase = nomeBase.replace(/\b\d+[\.,]?\d*\s?(kg|g|mg|l|ml|un|und)\b/gi, "");

                        let nomeNormalizado = normalizar(nomeBase);
                        let palavras = nomeNormalizado.split(/\s+/);

                        let marcasAPI = [];
                        if (produto.brands) {
                            marcasAPI = produto.brands
                                .split(",")
                                .map(m => normalizar(m))
                                .filter(m => m.length > 2);
                        }

                        const blacklist = [
                            "italac", "piracanjuba", "nestle", "itambe", "tirol", "batavo",
                            "garoto", "lacta", "hersheys", "arcor",
                            "marilan", "piraque", "bauducco",
                            "sadia", "perdigao", "seara",
                            "coca", "cocacola", "pepsi", "fanta", "sprite",
                            "quaker", "yoki", "camil",
                            "hemmer", "quero", "fugini",
                            "pilao", "melitta", "trescoracoes",
                            "tradicional", "original"
                        ].map(normalizar);

                        const embalagens = [
                            "sache", "pacote", "lata", "pet", "garrafa", "caixa", "frasco"
                        ];

                        const stopWords = [
                            "de", "da", "do", "das", "dos", "para", "com", "sem"
                        ];

                        palavras = palavras.filter(p => {
                            if (p.length <= 2) return false;
                            if (/\d/.test(p)) return false;
                            if (stopWords.includes(p)) return false;
                            if (embalagens.includes(p)) return false;
                            if (marcasAPI.includes(p)) return false;
                            if (blacklist.includes(p)) return false;
                            if (marcasAPI.some(m => p.includes(m))) return false;
                            if (blacklist.some(m => p.includes(m))) return false;
                            return true;
                        });

                        if (palavras.length === 0 && produto.categories) {
                            const categoriaPrincipal = produto.categories.split(",")[0];
                            palavras = normalizar(categoriaPrincipal)
                                .split(/\s+/)
                                .filter(p => p.length > 2)
                                .slice(0, 3);
                        }

                        palavras = palavras.slice(0, 3);

                        let nomeProduto = capitalizar(palavras.join(" ").trim());
                        if (!nomeProduto) nomeProduto = "Produto";

                        let quantidadeExtraida = "";
                        let unidadeExtraida = "";

                        if (produto.quantity) {
                            const match = produto.quantity.match(
                                /(\d+[\.,]?\d*)\s*(kg|g|mg|l|ml|un|und)/i
                            );
                            if (match) {
                                quantidadeExtraida = match[1].replace(",", ".");
                                unidadeExtraida = match[2].toLowerCase();
                            }
                        }

                        setNomeDigitado(nomeProduto);
                        setQuantidade(quantidadeExtraida || 1);
                        setUnidade(unidadeExtraida || "");
                        setIngredienteSelecionado(null);

                    } catch (erro) {
                        console.error(erro);
                        alert("Erro ao buscar produto.");
                    }
                });

                timerRef.current = setInterval(() => {
                    setTempoRestante(t => {
                        if (t <= 1) {
                            alert("Tempo esgotado. Use o cadastro manual.");
                            encerrarCamera();
                            return 0;
                        }
                        return t - 1;
                    });
                }, 1000);
            });

        } catch (e) {
            console.error(e);
            alert("Erro inesperado ao iniciar a câmera.");
            encerrarCamera();
        }
    }

    function encerrarCamera() {
        try {
            Quagga.offDetected();
            Quagga.stop();
        } catch { }

        clearInterval(timerRef.current);
        quaggaAtivoRef.current = false;
        setCameraAtiva(false);
    }

    function salvarProdutoEscaneado() {
        if (!produtoEscaneado) return;

        const novoItem = {
            nome: produtoEscaneado.nome,
            quantidade: Number(produtoEscaneado.quantidade),
            unidade: produtoEscaneado.unidade
        };

        const novoEstoque = [...estoque, novoItem];

        setEstoque(novoEstoque);
        enviarEstoqueParaAPI(novoEstoque);

        setProdutoEscaneado(null);
        setSugestoesIngredientes([]);
    }

    return (
        <div style={{ padding: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
                <h2>📦 Estoque</h2>

                <button onClick={() => {
                    setModoHistorico(!modoHistorico);
                    const salvo = localStorage.getItem("estoque_historico");
                    setHistorico(salvo ? JSON.parse(salvo) : []);
                }}>
                    {modoHistorico ? "⬅ Voltar ao Estoque" : "📜 Ver Histórico"}
                </button>
            </div>

            {!modoHistorico && (
                <>
                    <input
                        placeholder="Digite o ingrediente"
                        value={nomeDigitado}
                        onChange={(e) => {
                            setNomeDigitado(e.target.value);
                            setIngredienteSelecionado(null);
                        }}
                    />

                    {nomeDigitado && !ingredienteSelecionado && (
                        <div style={listaSugestoes}>
                            {sugestoes.map((nome, index) => (
                                <div
                                    key={index}
                                    style={itemSugestao}
                                    onClick={() => {
                                        setIngredienteSelecionado({
                                            nome,
                                            unidades: unidadesBanco
                                        });
                                        setNomeDigitado(nome);
                                        setUnidade(unidadesBanco[0] || "");
                                    }}
                                >
                                    {nome}
                                </div>
                            ))}
                        </div>
                    )}
                    <input
                        type="number"
                        min="1"
                        placeholder="N° de pacotes"
                        value={numeroPacotes}
                        onChange={(e) => {
                            const valor = e.target.value;

                            if (valor === "") {
                                setNumeroPacotes("");
                                return;
                            }

                            const numero = Number(valor);

                            if (numero >= 1) {
                                setNumeroPacotes(numero);
                            }
                        }}
                    />
                    <input
                        type="number"
                        placeholder="Quantidade"
                        value={quantidade}
                        onChange={(e) => setQuantidade(e.target.value)}
                    />

                    <select
                        value={unidade}
                        onChange={(e) => setUnidade(e.target.value)}
                        disabled={!ingredienteSelecionado}
                    >
                        <option value="">Selecione a unidade</option>
                        {ingredienteSelecionado?.unidades.map((u, index) => (
                            <option key={index} value={u}>{u}</option>
                        ))}
                    </select>

                    <div style={{ display: "flex", gap: 8 }}>
                        <button onClick={adicionarItem} disabled={!ingredienteSelecionado}>
                            Salvar
                        </button>

                        <button onClick={iniciarLeituraCodigo}>
                            📷
                        </button>
                    </div>

                    <button
                        onClick={limparEstoque}
                        style={{ marginTop: 8, background: "red", color: "white" }}
                    >
                        Limpar Estoque
                    </button>

                    <hr />

                    {estoque.map((e, index) => (
                        <div key={index} style={linha}>
                            <span>{e.nome} — {e.quantidade} {e.unidade}</span>
                            <button onClick={() => removerItem(index)}>🗑️</button>
                        </div>
                    ))}
                </>
            )}

            {modoHistorico && (
                <>
                    <h3>📊 Histórico pós-cardápio</h3>

                    <button
                        onClick={limparHistorico}
                        style={{ background: "red", color: "white", marginBottom: 12 }}
                    >
                        Limpar Histórico
                    </button>

                    {historico.length === 0 && <p>Nenhum histórico disponível.</p>}

                    {historico.map((e, index) => (
                        <div key={index} style={linha}>
                            <span>{e.nome} — {e.quantidade} {e.unidade}</span>
                        </div>
                    ))}
                </>
            )}

            {cameraAtiva && (
                <div style={overlay}>
                    <div style={cameraBox}>
                        <p>📷 Aponte para o código ({tempoRestante}s)</p>
                        <div id="camera" style={{ width: 280, height: 200 }} />
                        <button onClick={encerrarCamera}>Cancelar</button>
                    </div>
                </div>
            )}

            {produtoEscaneado && (
                <div style={overlay}>
                    <div style={cameraBox}>
                        <h3>Produto Reconhecido</h3>

                        {/* ========================= */}
                        {/* 🔥 NOME COM AUTOCOMPLETE IGUAL AO MANUAL */}
                        {/* ========================= */}

                        <div style={{ marginBottom: 8, position: "relative" }}>
                            <label>Ingrediente</label>
                            <input
                                type="text"
                                value={produtoEscaneado.nome}
                                autoComplete="off"
                                onChange={(e) => {
                                    const valor = e.target.value;

                                    setProdutoEscaneado({
                                        ...produtoEscaneado,
                                        nome: valor
                                    });

                                    if (valor.length >= 1) {
                                        const filtrados = ingredientesBanco
                                            .filter(item =>
                                                item.nome
                                                    .toLowerCase()
                                                    .includes(valor.toLowerCase())
                                            )
                                            .slice(0, 4);

                                        setSugestoesIngredientes(filtrados);
                                    } else {
                                        setSugestoesIngredientes([]);
                                    }
                                }}
                            />

                            {/* 🔥 LISTA IGUAL AO MANUAL */}
                            {sugestoesIngredientes.length > 0 && (
                                <div
                                    style={{
                                        position: "absolute",
                                        background: "#fff",
                                        border: "1px solid #ccc",
                                        width: "100%",
                                        maxHeight: 120,
                                        overflowY: "auto",
                                        zIndex: 999
                                    }}
                                >
                                    {sugestoesIngredientes.map((item, index) => (
                                        <div
                                            key={index}
                                            style={{
                                                padding: 6,
                                                cursor: "pointer"
                                            }}
                                            onClick={() => {
                                                setProdutoEscaneado({
                                                    ...produtoEscaneado,
                                                    nome: item.nome,
                                                    unidade: item.unidade
                                                });

                                                setSugestoesIngredientes([]);
                                            }}
                                        >
                                            {item.nome}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* ========================= */}
                        {/* 🔥 QUANTIDADE */}
                        {/* ========================= */}

                        <div style={{ marginBottom: 8 }}>
                            <label>Quantidade</label>
                            <input
                                type="number"
                                value={produtoEscaneado.quantidade}
                                onChange={(e) =>
                                    setProdutoEscaneado({
                                        ...produtoEscaneado,
                                        quantidade: e.target.value
                                    })
                                }
                            />
                        </div>

                        {/* ========================= */}
                        {/* 🔥 UNIDADE IGUAL AO MANUAL */}
                        {/* ========================= */}

                        <div style={{ marginBottom: 8 }}>
                            <label>Unidade</label>
                            <select
                                value={produtoEscaneado.unidade}
                                onChange={(e) =>
                                    setProdutoEscaneado({
                                        ...produtoEscaneado,
                                        unidade: e.target.value
                                    })
                                }
                            >
                                <option value="">Selecione</option>
                                {[
                                    ...new Set(ingredientesBanco.map(item => item.unidade))
                                ].map((uni, index) => (
                                    <option key={index} value={uni}>
                                        {uni}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* ========================= */}
                        {/* 🔥 BOTÕES COM VALIDAÇÃO */}
                        {/* ========================= */}

                        <div style={{ display: "flex", gap: 8 }}>
                            <button
                                onClick={() => {
                                    const ingredienteExiste = ingredientesBanco.find(
                                        item =>
                                            item.nome.toLowerCase() ===
                                            produtoEscaneado.nome.toLowerCase()
                                    );

                                    if (!ingredienteExiste) {
                                        alert(
                                            "Esse ingrediente não está registrado no nosso banco de receitas."
                                        );
                                        return;
                                    }

                                    if (!produtoEscaneado.quantidade) {
                                        alert("Informe a quantidade.");
                                        return;
                                    }

                                    salvarProdutoEscaneado();
                                }}
                            >
                                Salvar
                            </button>

                            <button
                                onClick={() => {
                                    setProdutoEscaneado(null);
                                    setSugestoesIngredientes([]);
                                }}
                            >
                                Cancelar
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

const linha = {
    display: "flex",
    justifyContent: "space-between",
    marginBottom: 8,
    border: "1px solid #ddd",
    padding: 8,
    borderRadius: 6,
};

const listaSugestoes = {
    border: "1px solid #ccc",
    borderRadius: 6,
    marginBottom: 8,
    maxHeight: 150,
    overflowY: "auto"
};

const itemSugestao = {
    padding: 8,
    cursor: "pointer",
    borderBottom: "1px solid #eee"
};

const overlay = {
    position: "fixed",
    inset: 0,
    background: "rgba(0,0,0,0.6)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 999
};

const cameraBox = {
    background: "#fff",
    padding: 16,
    borderRadius: 8,
    textAlign: "center"
};