import { useState } from "react";
import ModalEditarCampo from "../components/ModalEditarCampo";
import "../components/Perfil.css";

/* =========================
   TEXTOS EXPLICATIVOS
========================= */
const isPremium = localStorage.getItem("isPremium") === "true";

const explicacoes = {
    nome: "Seu nome ou apelido usado apenas dentro do aplicativo.",
    idade: "Ajuda a estimar necessidades nutricionais e energéticas.",
    sexo: "Influência em cálculos metabólicos e hormonais.",
    altura: "Usada para cálculo de IMC e estimativas corporais.",
    peso: "Ajuda a acompanhar evolução corporal ao longo do tempo.",
    atividade: "Define seu gasto calórico diário.",
    cintura: "Indicador de gordura abdominal e risco metabólico.",
    quadril: "Usado junto da cintura para avaliar distribuição de gordura.",
    pescoco: "Auxilia na estimativa de gordura corporal.",
    gordura: "Percentual estimado de gordura corporal, se você souber.",

    imc: "Índice de Massa Corporal. Relação entre peso e altura.",
    imcClass: "Classificação baseada nos critérios da OMS.",
    tmb: "Taxa Metabólica Basal. Energia mínima para funções vitais.",
    get: "Gasto Energético Total diário estimado.",
    macros: `Distribuição estimada de macronutrientes:

C = Carboidratos (energia)
P = Proteínas (músculos e recuperação)
G = Gorduras (hormônios e absorção de vitaminas)

Valores diários estimados com base no seu perfil.`,
    rcq: "Relação entre cintura e quadril.",
    pesoIdeal: "Peso estimado com base em IMC saudável.",
    idadeMeta: "Estimativa comparativa do metabolismo.",
};

/* =========================
   FATOR ATIVIDADE
========================= */
const fatorAtividade = {
    sedentario: 1.2,
    leve: 1.375,
    moderado: 1.55,
    alto: 1.725,
    extremo: 1.9,
};

export default function Perfil() {
    const [perfil, setPerfil] = useState(
        () => JSON.parse(localStorage.getItem("perfil_usuario")) || {}
    );
    const [campoEditando, setCampoEditando] = useState(null);
    const [campoInfo, setCampoInfo] = useState(null);
    const [subAba, setSubAba] = useState("perfil");

    /* =========================
       FUNÇÕES
    ========================= */
    function salvarCampo(campo, valor) {
        if (valor === undefined || valor === null) return;

        // remove caracteres proibidos
        const proibidos = /[<>´~;\]\[\=\-,]/g;
        let valorFinal = String(valor).replace(proibidos, "");

        // campos que devem ser número
        const camposNumericos = [
            "idade",
            "altura",
            "peso",
            "cintura",
            "quadril",
            "pescoco",
            "gordura",
        ];

        if (camposNumericos.includes(campo)) {
            valorFinal = Number(valorFinal);
            if (isNaN(valorFinal)) return;
        }

        const novoPerfil = {
            ...perfil,
            [campo]: valorFinal,
        };

        localStorage.setItem("perfil_usuario", JSON.stringify(novoPerfil));
        setPerfil(novoPerfil);
        setCampoEditando(null);
    }

    function abrirEdicao(config) {
        setCampoEditando(config);
    }

    function linha(label, campo, unidade = "", tipo = "text", opcoes = null) {
        const valorExibido =
            campo === "atividade"
                ? {
                    sedentario: "Sedentário",
                    leve: "Levemente ativo",
                    moderado: "Moderadamente ativo",
                    alto: "Muito ativo",
                    extremo: "Extremamente ativo",
                }[perfil[campo]]
                : perfil[campo];

        return (
            <div className="hp-linha">
                <div style={labelContainer}>
                    <strong>{label}</strong>
                    <button className="hp-btn-info" onClick={() => setCampoInfo(campo)}>
                        ?
                    </button>
                    <span>
                        {valorExibido !== undefined && valorExibido !== null
                            ? ` ${valorExibido} ${unidade}`
                            : " —"}
                    </span>
                </div>

                <button
                    onClick={() =>
                        abrirEdicao({
                            campo,
                            tipo,
                            opcoes,
                        })
                    }
                    className="hp-btn-icon"
                >
                    ✏️
                </button>
            </div>
        );
    }

    function fichaLinha(label, valor, chave, unidade = "") {
        return (
            <div className="hp-linha">
                <strong>
                    {label}
                    <button
                        className="hp-btn-info"
                        onClick={() => setCampoInfo(chave)}
                    >
                        ?
                    </button>
                </strong>
                <span style={{ whiteSpace: "pre-line", textAlign: "right" }}>
                    {valor !== null && valor !== undefined
                        ? `${valor} ${unidade}`
                        : "—"}
                </span>
            </div>
        );
    }

    /* =========================
       CÁLCULOS
    ========================= */
    const alturaM = perfil.altura ? perfil.altura / 100 : null;

    const imc =
        perfil.peso && alturaM
            ? (perfil.peso / (alturaM * alturaM)).toFixed(1)
            : null;

    let imcClass = null;
    if (imc) {
        if (imc < 18.5) imcClass = "Abaixo do peso";
        else if (imc < 25) imcClass = "Peso normal";
        else if (imc < 30) imcClass = "Sobrepeso";
        else imcClass = "Obesidade";
    }

    const sexo = perfil.sexo?.toLowerCase();

    const tmb =
        perfil.peso && perfil.altura && perfil.idade && sexo
            ? sexo === "masculino"
                ? Math.round(
                    10 * perfil.peso +
                    6.25 * perfil.altura -
                    5 * perfil.idade +
                    5
                )
                : Math.round(
                    10 * perfil.peso +
                    6.25 * perfil.altura -
                    5 * perfil.idade -
                    161
                )
            : null;

    const get =
        tmb && perfil.atividade
            ? Math.round(
                tmb *
                (fatorAtividade[perfil.atividade] ||
                    fatorAtividade.sedentario)
            )
            : null;

    const macros = get
        ? {
            carbo: Math.round((get * 0.5) / 4),
            proteina: Math.round((get * 0.25) / 4),
            gordura: Math.round((get * 0.25) / 9),
        }
        : null;

    const rcq =
        perfil.cintura && perfil.quadril
            ? (perfil.cintura / perfil.quadril).toFixed(2)
            : null;

    const pesoIdeal = alturaM
        ? (22 * alturaM * alturaM).toFixed(1)
        : null;

    const idadeMeta =
        tmb && perfil.idade
            ? tmb < (sexo === "masculino" ? 1600 : 1400)
                ? "Acima da idade real"
                : "Compatível com a idade"
            : null;

    return (
        <div>
            {/* HEADER */}

            <div className="hp-perfil-header">
                <h2>👤 Perfil</h2>

                <div className="hp-subabas">

                    {/* DADOS */}
                    <button
                        className={`hp-subaba-btn ${subAba === "perfil" ? "hp-subaba-ativa" : ""
                            }`}
                        onClick={() => setSubAba("perfil")}
                    >
                        Dados
                    </button>

                    {/* FICHA */}
                    <button
                        className={`hp-subaba-btn ${subAba === "ficha" && isPremium ? "hp-subaba-ativa" : ""
                            } ${!isPremium ? "hp-subaba-bloqueada" : ""}`}
                        onClick={() => {
                            if (isPremium) setSubAba("ficha");
                        }}
                        title={
                            isPremium
                                ? "Ficha nutricional"
                                : "Disponível apenas para conta Premium"
                        }
                    >
                        📋 Ficha nutricional
                    </button>

                </div>
            </div>

            {/* SUBABAS */}
            {subAba === "perfil" && (
                <>
                    {linha("Nome", "nome")}
                    {linha("Idade", "idade", "anos")}
                    {linha(
                        "Sexo",
                        "sexo",
                        "",
                        "select",
                        [
                            { value: "masculino", label: "Masculino" },
                            { value: "feminino", label: "Feminino" },
                            { value: "nao_informar", label: "Prefiro não informar" },
                        ]
                    )}
                    {linha("Altura", "altura", "cm")}
                    {linha("Peso", "peso", "kg")}
                    {linha(
                        "Nível de atividade",
                        "atividade",
                        "",
                        "select",
                        [
                            { value: "sedentario", label: "Sedentário" },
                            { value: "leve", label: "Levemente ativo" },
                            { value: "moderado", label: "Moderadamente ativo" },
                            { value: "alto", label: "Muito ativo" },
                            { value: "extremo", label: "Extremamente ativo" },
                        ]
                    )}
                    {linha("Cintura", "cintura", "cm")}
                    {linha("Quadril", "quadril", "cm")}
                    {linha("Pescoço", "pescoco", "cm")}
                    {linha("Gordura corporal", "gordura", "%")}
                </>
            )}

            {subAba === "ficha" && (
                <div className="hp-ficha">
                    {fichaLinha("IMC", imc, "imc")}
                    {fichaLinha("Classificação IMC", imcClass, "imcClass")}
                    {fichaLinha("TMB", tmb, "tmb", "kcal")}
                    {fichaLinha("GET", get, "get", "kcal")}
                    {fichaLinha(
                        "Macronutrientes",
                        macros
                            ? `${macros.carbo}g C\n${macros.proteina}g P\n${macros.gordura}g G`
                            : null,
                        "macros"
                    )}
                    {fichaLinha(
                        "Relação Cintura–Quadril",
                        rcq,
                        "rcq"
                    )}
                    {fichaLinha(
                        "Peso ideal estimado",
                        pesoIdeal,
                        "pesoIdeal",
                        "kg"
                    )}
                    {fichaLinha(
                        "Idade metabólica",
                        idadeMeta,
                        "idadeMeta"
                    )}
                </div>
            )}

            {/* MODAIS */}
            {campoEditando && (
                <ModalEditarCampo
                    campo={campoEditando.campo}
                    tipo={campoEditando.tipo}
                    opcoes={campoEditando.opcoes}
                    valorAtual={perfil[campoEditando.campo]}
                    onSalvar={salvarCampo}
                    onCancelar={() => setCampoEditando(null)}
                />
            )}

            {campoInfo && (
                <div style={overlay}>
                    <div className="hp-modal-info">
                        <h3>ℹ️ O que é isso?</h3>
                        <p style={{ whiteSpace: "pre-line" }}>
                            {explicacoes[campoInfo]}
                        </p>
                        <button
                            className="hp-btn"
                            onClick={() => setCampoInfo(null)}
                        >
                            Fechar
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
