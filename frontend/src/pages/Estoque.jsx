import { useState, useEffect, useRef } from "react";
import Quagga from "quagga";
import { Camera, CameraResultType } from '@capacitor/camera';
import "../components/Estoque.css";
import EstoqueTwoIcon from "../assets/icons/EstoqueTwoIcon.png";
import HistoricoIcon from "../assets/icons/HistoricoIcon.png";
import CameraIcon from "../assets/icons/CameraIcon.png";
import DeleteIcon from "../assets/icons/DeleteIcon.png";
import jsQR from "jsqr";


const BASE_URL = "https://prealpha.onrender.com"

export default function Estoque() {
    const [nomeDigitado, setNomeDigitado] = useState("");
    const [ingredienteSelecionado, setIngredienteSelecionado] = useState(null);

    const [novoIngrediente, setNovoIngrediente] = useState(null);
    const [categoriaSelecionada, setCategoriaSelecionada] = useState("");

    const [quantidade, setQuantidade] = useState("");
    const [unidade, setUnidade] = useState("");
    const [numeroPacotes, setNumeroPacotes] = useState(1);

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
    const [tempoRestante, setTempoRestante] = useState(30);
    const [produtoEscaneado, setProdutoEscaneado] = useState(null);

    const timerRef = useRef(null);
    const quaggaAtivoRef = useRef(false);

    useEffect(() => {
        fetch(`${BASE_URL}/ingredientes`)
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

    function normalizarTexto(texto) {
        if (!texto) return "";

        return texto
            .toLowerCase()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .trim();
    }

    function nomeValido(texto) {
        return /^[A-Za-zÀ-ÿ\s]+$/.test(texto.trim());
    }

    function adicionarItem() {
        if (!nomeDigitado.trim() || !quantidade || Number(quantidade) <= 0 || !unidade) {
            alert("Preencha todos os campos corretamente.");
            return;
        }

        if (!numeroPacotes || Number(numeroPacotes) < 1) {
            alert("Informe o N° de pacotes (mínimo 1).");
            return;
        }

        const existe = ingredientesCompletos.some(
            item =>
                normalizarTexto(item) === normalizarTexto(nomeDigitado)
        );

        if (!existe) {
            if (!nomeValido(nomeDigitado)) {
                alert("Nome inválido. Use apenas letras.");
                return;
            }

            setNovoIngrediente(nomeDigitado);
            return; // 🔥 abre modal
        }

        const quantidadeFinal = Number(quantidade) * Number(numeroPacotes);

        const novoEstoque = [
            ...estoque,
            {
                nome: nomeDigitado,
                quantidade: quantidadeFinal,
                unidade
            }
        ];

        setEstoque(novoEstoque);
        enviarEstoqueParaAPI(novoEstoque);

        // reset
        setNomeDigitado("");
        setQuantidade("");
        setUnidade("");
        setNumeroPacotes(1);
    }


    const [notaFiscal, setNotaFiscal] = useState(null);
    const [itensSelecionados, setItensSelecionados] = useState([]);


    function detectarQRCode(video) {
        if (!video || video.videoWidth === 0 || video.videoHeight === 0) {
            return null;
        }

        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        try {
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const code = jsQR(imageData.data, canvas.width, canvas.height);
            return code ? code.data : null;
        } catch {
            return null;
        }
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
        fetch(`${BASE_URL}/estoque`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ estoque: novoEstoque })
        });
    }

    const categoriasDisponiveis = [
        "proteinasKG",
        "proteinasUN",
        "proteinasCF",
        "carboidratosCF",
        "frutas",
        "liquidos",
        "cereais",
        "fermentos",
        "produtoBruto",
        "farinhas",
        "folhas_saladas",
        "carboidratos",
        "massas",
        "molhos",
        "caldos",
        "legumes"
    ];

    const [ingredientesCustom, setIngredientesCustom] = useState(() => {
        const salvo = localStorage.getItem("ingredientes_custom");
        return salvo ? JSON.parse(salvo) : {};
    });

    const ingredientesCompletos = [
        ...ingredientesBanco,
        ...Object.values(ingredientesCustom || {}).flat()
    ];

    const sugestoes = nomeDigitado
        ? ingredientesCompletos
            .filter(item =>
                normalizarTexto(item).includes(normalizarTexto(nomeDigitado))
            )
            .slice(0, 5)
        : [];

    // ============================
    // 🔥 NOVOS STATES (ADICIONE JUNTO AOS OUTROS STATES DO COMPONENTE)
    // ============================

    const [mostrarAvisoIngrediente, setMostrarAvisoIngrediente] = useState(false);
    const [sugestoesIngredientes, setSugestoesIngredientes] = useState([]);

    const deviceIdRef = useRef(null);

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

    function toggleItemSelecionado(index) {
        setItensSelecionados(prev => {
            if (prev.includes(index)) {
                return prev.filter(i => i !== index);
            } else {
                return [...prev, index];
            }
        });
    }

    function adicionarItensNotaAoEstoque() {
        if (!notaFiscal) return;

        const itensEscolhidos = itensSelecionados.map(i => notaFiscal.itens[i]);

        const novosItens = itensEscolhidos
            .filter(item => item.nome && item.quantidade && item.unidade)
            .map(item => ({
                nome: item.nome,
                quantidade: item.quantidade,
                unidade: item.unidade
            }));

        if (novosItens.length === 0) {
            alert("Nenhum item válido selecionado.");
            return;
        }

        const novoEstoque = [...estoque, ...novosItens];

        setEstoque(novoEstoque);
        enviarEstoqueParaAPI(novoEstoque);

        // limpa estado
        setNotaFiscal(null);
        setItensSelecionados([]);
    }

    // ============================
    // 🔥 SUA FUNÇÃO ORIGINAL (NÃO REMOVIDO NADA)
    // ============================
    async function solicitarPermissao() {
        const permission = await Camera.requestPermissions();
        return permission.camera === "granted";
    }


    function iniciarQuagga(constraints, target) {
        return new Promise((resolve, reject) => {
            Quagga.init(
                {
                    inputStream: {
                        type: "LiveStream",
                        target,
                        constraints
                    },
                    locator: { patchSize: "medium", halfSample: true },
                    numOfWorkers: navigator.hardwareConcurrency || 4,
                    frequency: 30,
                    decoder: { readers: ["ean_reader"] },
                    locate: true
                },
                err => {
                    if (err) return reject(err);
                    Quagga.start();
                    resolve();
                }
            );
        });
    }


    async function processarQRCode(url) {
        try {
            const res = await fetch(`${BASE_URL}/nota-fiscal/ler`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ url })
            });

            const data = await res.json();

            if (!data || !data.itens || data.itens.length === 0) {
                alert("Nenhum item encontrado na nota.");
                return;
            }

            setNotaFiscal(data);
            setItensSelecionados([]);

        } catch (e) {
            console.error(e);
            alert("Erro ao processar QR Code");
        }
    }

    async function iniciarLeituraCodigo() {
        if (quaggaAtivoRef.current) return;

        const permitido = await solicitarPermissao();

        if (!permitido) {
            alert("Permissão de câmera negada.");
            return;
        }

        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            const cameras = devices.filter(d => d.kind === "videoinput");

            if (cameras.length === 0) {
                alert("Nenhuma câmera encontrada.");
                return;
            }

            setCameraAtiva(true);
            setTempoRestante(30);
            quaggaAtivoRef.current = true;

            requestAnimationFrame(async function initCamera() {
                const target = document.querySelector("#camera");

                if (!target) {
                    alert("Erro ao acessar elemento da câmera.");
                    encerrarCamera();
                    return;
                }

                let constraints;

                try {
                    if (deviceIdRef.current) {
                        constraints = {
                            deviceId: { exact: deviceIdRef.current }
                        };
                    } else {
                        constraints = {
                            facingMode: { exact: "environment" }
                        };
                    }

                    await iniciarQuagga(constraints, target);

                } catch (erroFacing) {
                    console.warn("Fallback câmera...", erroFacing);

                    try {
                        let cameraPreferida =
                            cameras.find(device =>
                                device.label.toLowerCase().includes("back") ||
                                device.label.toLowerCase().includes("traseira") ||
                                device.label.toLowerCase().includes("environment")
                            ) || cameras[cameras.length - 1];

                        deviceIdRef.current = cameraPreferida.deviceId;

                        constraints = {
                            deviceId: { exact: cameraPreferida.deviceId }
                        };

                        await iniciarQuagga(constraints, target);

                    } catch (erroFinal) {
                        console.error(erroFinal);
                        alert("Erro ao iniciar a câmera.");
                        encerrarCamera();
                        return;
                    }
                }

                // =========================
                // 🔥 QR CODE LOOP
                // =========================
                function scanQRCodeLoop() {
                    if (!quaggaAtivoRef.current) return;

                    const video = target.querySelector("video");

                    if (video && video.readyState === 4) {
                        const qr = detectarQRCode(video);

                        if (qr && qr.startsWith("http")) {
                            console.log("QR detectado:", qr);

                            quaggaAtivoRef.current = false; // 🔥 trava tudo
                            encerrarCamera();
                            processarQRCode(qr);
                            return;
                        }
                    }

                    requestAnimationFrame(scanQRCodeLoop);
                }

                scanQRCodeLoop();

                // =========================
                // 🔥 BARCODE (SEU CÓDIGO ORIGINAL)
                // =========================
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

                // =========================
                // ⏱️ TIMER
                // =========================
                timerRef.current = setInterval(() => {
                    setTempoRestante(t => {
                        if (t <= 1) {
                            alert("Tempo esgotado.");
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
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <h2 className="hp-titulo"> <img src={EstoqueTwoIcon} /> Estoque </h2>

                <button className="hp-subaba-btn" onClick={() => {
                    setModoHistorico(!modoHistorico);
                    const salvo = localStorage.getItem("estoque_historico");
                    setHistorico(salvo ? JSON.parse(salvo) : []);
                }}>
                    <img
                        src={modoHistorico ? EstoqueTwoIcon : HistoricoIcon}
                        alt=""
                        className="hp-icon"
                    />
                    {modoHistorico ? "Voltar" : "Histórico"}
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

                    {mostrarAvisoIngrediente && (
                        <p className="hp-erro">
                            Ingrediente não encontrado no banco.
                        </p>
                    )}

                    {nomeDigitado && !ingredienteSelecionado && (
                        <div className="hp-sugestoes">
                            {sugestoes.map((item, index) => (
                                <div
                                    key={index}
                                    className="hp-sugestao-item"
                                    onClick={() => {
                                        setIngredienteSelecionado(item);
                                        setNomeDigitado(item);
                                    }}
                                >
                                    {item}
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
                    >
                        <option value="">Selecione a unidade</option>
                        {unidadesBanco.map((u, index) => (
                            <option key={index} value={u}>{u}</option>
                        ))}
                    </select>

                    <div style={{ display: "flex", gap: 8 }}>
                        <button className="hp-btn-save" onClick={adicionarItem}>
                            Salvar
                        </button>

                        <button onClick={iniciarLeituraCodigo}>
                            <img
                                src={CameraIcon}
                                alt=""
                                className="hp-icon"
                            />
                        </button>
                    </div>

                    <button
                        className="hp-btn-danger"
                        onClick={limparEstoque}
                    >
                        Limpar Estoque
                    </button>
                    <hr />

                    {estoque.map((e, index) => (
                        <div key={index} className="hp-estoque-linha">
                            <span>{e.nome} — {e.quantidade} {e.unidade}</span>
                            <button onClick={() => removerItem(index)}>
                                <img
                                    src={DeleteIcon}
                                    alt=""
                                    className="hp-icon"
                                />
                            </button>
                        </div>
                    ))}
                </>
            )}

            {modoHistorico && (
                <>
                    <h3>Histórico pós-cardápio</h3>

                    <button
                        onClick={limparHistorico}
                        className="hp-btn-danger"
                    >
                        Limpar Histórico
                    </button>

                    {historico.length === 0 && <p>Nenhum histórico disponível.</p>}

                    {historico.map((e, index) => (
                        <div key={index} className="hp-estoque-linha">
                            <span>{e.nome} — {e.quantidade} {e.unidade}</span>
                        </div>
                    ))}
                </>
            )}

            {cameraAtiva && (
                <div className="hp-overlay">
                    <div className="hp-camera-box">
                        <p><img src={CameraIcon} alt="" className="hp-icon" /> Aponte para o código ({tempoRestante}s)</p>
                        <div id="camera" className="hp-camera" />
                        <button onClick={encerrarCamera}>Cancelar</button>
                    </div>
                </div>
            )}

            {produtoEscaneado && (
                <div className="hp-overlay">
                    <div className="hp-camera-box">
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
                                                item
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
                                                    nome: item
                                                });

                                                setSugestoesIngredientes([]);
                                            }}
                                        >
                                            {item}
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
                                {
                                    unidadesBanco.map((uni, index) => (
                                        <option key={index} value={uni}>
                                            {uni}
                                        </option>
                                    ))
                                }
                            </select>
                        </div>

                        {/* ========================= */}
                        {/* 🔥 BOTÕES COM VALIDAÇÃO */}
                        {/* ========================= */}

                        <div style={{ display: "flex", gap: 8 }}>
                            <button
                                onClick={() => {
                                    const ingredienteExiste = ingredientesBanco.some(normalizarTexto(item) === normalizarTexto(produtoEscaneado.nome));

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

            {notaFiscal && (
                <div className="hp-overlay">
                    <div className="hp-camera-box" style={{ maxHeight: "80vh", overflowY: "auto" }}>

                        <h3>Nota Fiscal</h3>

                        <p><strong>Mercado:</strong> {notaFiscal.mercado || "Não identificado"}</p>
                        <p><strong>Data:</strong> {notaFiscal.data || "Não identificada"}</p>

                        <hr />

                        <h4>Itens encontrados</h4>

                        {notaFiscal.itens.length === 0 && (
                            <p>Nenhum item encontrado.</p>
                        )}

                        {notaFiscal.itens.map((item, index) => (
                            <div
                                key={index}
                                style={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: 8,
                                    padding: 6,
                                    borderBottom: "1px solid #eee"
                                }}
                            >
                                <input
                                    type="checkbox"
                                    checked={itensSelecionados.includes(index)}
                                    onChange={() => toggleItemSelecionado(index)}
                                />

                                <div>
                                    <div><strong>{item.nome}</strong></div>

                                    <div style={{ fontSize: 12, opacity: 0.7 }}>
                                        {item.quantidade || "?"} {item.unidade || ""}
                                        {item.preco_total && (
                                            <> — R$ {item.preco_total}</>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}

                        <hr />

                        <div style={{ display: "flex", gap: 8 }}>
                            <button onClick={adicionarItensNotaAoEstoque}>
                                Adicionar ao estoque
                            </button>

                            <button onClick={() => {
                                setNotaFiscal(null);
                                setItensSelecionados([]);
                            }}>
                                Cancelar
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {novoIngrediente && (
                <div className="hp-overlay">
                    <div className="hp-modal">

                        <h3>Novo ingrediente</h3>

                        <p><strong>{novoIngrediente}</strong> não existe.</p>

                        <select
                            value={categoriaSelecionada}
                            onChange={(e) => setCategoriaSelecionada(e.target.value)}
                        >
                            <option value="">Selecione a categoria</option>

                            {categoriasDisponiveis.map((cat, i) => (
                                <option key={i} value={cat}>
                                    {cat}
                                </option>
                            ))}
                        </select>

                        <div className="hp-flex">
                            <button
                                className="hp-btn"
                                onClick={() => {
                                    if (!categoriaSelecionada) {
                                        alert("Selecione a categoria");
                                        return;
                                    }

                                    const atualizado = {
                                        ...ingredientesCustom,
                                        [categoriaSelecionada]: [
                                            ...(ingredientesCustom[categoriaSelecionada] || []),
                                            novoIngrediente
                                        ]
                                    };

                                    setIngredientesCustom(atualizado);
                                    localStorage.setItem(
                                        "ingredientes_custom",
                                        JSON.stringify(atualizado)
                                    );

                                    setNovoIngrediente(null);
                                    setCategoriaSelecionada("");

                                    // 🔥 já adiciona no estoque automaticamente
                                    setIngredientesBanco(prev => [...prev, novoIngrediente]);
                                    setTimeout(() => {
                                        setNomeDigitado(novoIngrediente);
                                        adicionarItem();
                                    }, 0);

                                    if (!nomeValido(novoIngrediente)) {
                                        alert("Nome inválido. Apenas letras.");
                                        return;
                                    }
                                }}
                            >
                                Salvar
                            </button>

                            <button
                                className="hp-btn-secundario"
                                onClick={() => {
                                    setNovoIngrediente(null);
                                    setCategoriaSelecionada("");
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
