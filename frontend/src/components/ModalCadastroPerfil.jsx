import { useState } from "react";

export default function ModalCadastroPerfil({ onSalvar }) {
    const [form, setForm] = useState({
        nome: "",
        idade: "",
        sexo: "",
        altura: "",
        peso: "",
        atividade: "",
        cintura: "",
        quadril: "",
        pescoco: "",
        gordura: "",
    });

    function handleChange(e) {
        setForm({ ...form, [e.target.name]: e.target.value });
    }

    const podeSalvar =
        form.nome.trim() &&
        form.idade &&
        form.sexo;

    function salvar() {
        const perfil = {
            nome: form.nome.trim(),
            idade: Number(form.idade),
            sexo: form.sexo,

            altura: form.altura ? Number(form.altura) : null,
            peso: form.peso ? Number(form.peso) : null,

            atividade_fisica: form.atividade || null,

            medidas: {
                cintura: form.cintura ? Number(form.cintura) : null,
                quadril: form.quadril ? Number(form.quadril) : null,
                pescoco: form.pescoco ? Number(form.pescoco) : null,
                gordura_percentual: form.gordura ? Number(form.gordura) : null,
            },

            criado_em: new Date().toISOString(),
        };

        onSalvar(perfil);
    }

    return (
        <div style={overlay}>
            <div style={modal}>
                <h2>👤 Cadastro Inicial</h2>
                <p style={{ fontSize: 14, color: "#666" }}>
                    Precisamos de alguns dados básicos para continuar.
                </p>

                <div style={conteudo}>
                    <input name="nome" placeholder="Nome *" onChange={handleChange} />
                    <input name="idade" type="number" placeholder="Idade *" onChange={handleChange} />

                    <select name="sexo" onChange={handleChange}>
                        <option value="">Sexo biológico *</option>
                        <option value="masculino">Masculino</option>
                        <option value="feminino">Feminino</option>
                        <option value="nao_informar">Prefiro não informar</option>
                    </select>

                    <input name="altura" type="number" placeholder="Altura (cm)" onChange={handleChange} />
                    <input name="peso" type="number" placeholder="Peso (kg)" onChange={handleChange} />

                    <select name="atividade" onChange={handleChange}>
                        <option value="">Nível de atividade física</option>
                        <option value="sedentario">Sedentário</option>
                        <option value="levemente_ativo">Levemente ativo</option>
                        <option value="moderadamente_ativo">Moderadamente ativo</option>
                        <option value="muito_ativo">Muito ativo</option>
                        <option value="extremamente_ativo">Extremamente ativo</option>
                    </select>

                    <h4>Medidas corporais (opcional)</h4>

                    <input name="cintura" placeholder="Cintura (cm)" onChange={handleChange} />
                    <input name="quadril" placeholder="Quadril (cm)" onChange={handleChange} />
                    <input name="pescoco" placeholder="Pescoço (cm)" onChange={handleChange} />
                    <input name="gordura" placeholder="% Gordura estimado" onChange={handleChange} />
                </div>

                <button
                    disabled={!podeSalvar}
                    onClick={salvar}
                    style={{
                        ...botao,
                        background: podeSalvar ? "#28a745" : "#ccc",
                    }}
                >
                    💾 Salvar Perfil
                </button>
            </div>
        </div>
    );
}

/* ===== estilos ===== */

const overlay = {
    position: "fixed",
    inset: 0,
    background: "rgba(0,0,0,0.7)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 9999,
};

const modal = {
    background: "#fff",
    padding: 20,
    borderRadius: 12,
    width: "90%",
    maxWidth: 520,
};

const conteudo = {
    display: "flex",
    flexDirection: "column",
    gap: 10,
    maxHeight: 420,
    overflowY: "auto",
    marginBottom: 15,
};

const botao = {
    width: "100%",
    padding: 12,
    borderRadius: 8,
    border: "none",
    color: "#fff",
    fontSize: 16,
    cursor: "pointer",
};