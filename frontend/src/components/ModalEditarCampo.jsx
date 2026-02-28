import { useState, useEffect } from "react";

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
        <div style={overlay}>
            <div style={modal}>
                <h3>Editar</h3>

                {tipo === "select" ? (
                    <select
                        value={valor}
                        onChange={(e) => setValor(e.target.value)}
                        style={input}
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
                        style={input}
                    />
                )}

                {!valido && (
                    <p style={erro}>
                        {campo === "nome"
                            ? "Este campo aceita somente letras."
                            : "Este campo aceita somente números."}
                    </p>
                )}

                <div style={botoes}>
                    <button
                        onClick={() => onSalvar(campo, valor)}
                        disabled={!valido}
                        style={{
                            ...botaoSalvar,
                            opacity: valido ? 1 : 0.5,
                            cursor: valido ? "pointer" : "not-allowed",
                        }}
                    >
                        Salvar
                    </button>

                    <button onClick={onCancelar} style={botaoCancelar}>
                        Cancelar
                    </button>
                </div>
            </div>
        </div>
    );
}

/* =========================
   ESTILOS
========================= */

const overlay = {
    position: "fixed",
    inset: 0,
    background: "rgba(0,0,0,0.6)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 9999,
};

const modal = {
    background: "#fff",
    padding: 20,
    borderRadius: 10,
    width: "90%",
    maxWidth: 400,
};

const input = {
    width: "100%",
    padding: 10,
    marginBottom: 10,
};

const erro = {
    color: "#d32f2f",
    fontSize: 12,
    marginBottom: 10,
};

const botoes = {
    display: "flex",
    gap: 10,
};

const botaoSalvar = {
    flex: 1,
    padding: 10,
    background: "#4CAF50",
    color: "#fff",
    border: "none",
    borderRadius: 6,
};

const botaoCancelar = {
    flex: 1,
    padding: 10,
    background: "#ccc",
    border: "none",
    borderRadius: 6,
};