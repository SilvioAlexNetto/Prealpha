import { useState, useEffect } from "react";
import "./ModalEditarCampo.css";

/* =========================
   VALIDADORES
========================= */
function somenteNumeros(valor) {
    return /^[0-9]+$/.test(valor);
}

function somenteLetras(valor) {
    return /^[A-Za-zÀ-ÿ\s]+$/.test(valor);
}

export default function ModalEditarCampo({
    campo,
    tipo = "text",
    opcoes = [],
    valorAtual,
    onSalvar,
    onCancelar,
}) {
    const [valor, setValor] = useState(valorAtual || "");
    const [valido, setValido] = useState(true);

    /* =========================
       VALIDAÇÃO AUTOMÁTICA
    ========================= */
    useEffect(() => {
        // campos numéricos
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
            setValido(valor !== "" && somenteNumeros(valor));
            return;
        }

        // campo nome (somente letras)
        if (campo === "nome") {
            setValido(valor !== "" && somenteLetras(valor));
            return;
        }

        // select e outros campos
        setValido(true);
    }, [valor, campo]);

    return (
        <div className="hp-overlay">
            <div className="hp-modal-editar">
                <h3>Editar</h3>

                {tipo === "select" ? (
                    <select
                        value={valor}
                        onChange={(e) => setValor(e.target.value)}
                        className="hp-input"
                    >
                        <option value="">Selecione</option>
                        {opcoes.map((op) => (
                            <option key={op.value} value={op.value}>
                                {op.label}
                            </option>
                        ))}
                    </select>
                ) : (
                    <input
                        value={valor}
                        onChange={(e) => setValor(e.target.value)}
                        className="hp-input"
                    />
                )}

                {!valido && (
                    <p className="hp-erro">{erroMsg}
                        {campo === "nome"
                            ? "Este campo aceita somente letras."
                            : "Este campo aceita somente números."}
                    </p>
                )}

                <div className="hp-modal-botoes">
                    <button
                        onClick={() => onSalvar(campo, valor)}
                        disabled={!valido}
                        style={{
                            ...className = "hp-btn",
                            opacity: valido ? 1 : 0.5,
                            cursor: valido ? "pointer" : "not-allowed",
                        }}
                    >
                        Salvar
                    </button>

                    <button onClick={onCancelar} className="hp-btn-secundario">
                        Cancelar
                    </button>
                </div>
            </div>
        </div>
    );
}