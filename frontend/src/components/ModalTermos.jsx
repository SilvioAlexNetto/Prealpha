import { useState } from "react";

export default function ModalTermos({ onAceitar }) {
    const [scrollFinal, setScrollFinal] = useState(false);
    const [confirmado, setConfirmado] = useState(false);

    function handleScroll(e) {
        const { scrollTop, scrollHeight, clientHeight } = e.target;

        if (scrollTop + clientHeight >= scrollHeight - 5) {
            setScrollFinal(true);
        }
    }

    const podeAceitar = scrollFinal && confirmado;

    return (
        <div style={overlay}>
            <div style={modal}>
                <h2>📄 Termos e Condições de Uso</h2>

                <div style={conteudo} onScroll={handleScroll}>
                    {/* 1️⃣ Natureza do aplicativo */}
                    <h3>1. Natureza e Finalidade do Aplicativo</h3>
                    <p>
                        O aplicativo <strong>Health Pantry</strong> tem caráter exclusivamente
                        educativo, informativo e sugestivo, oferecendo sugestões gerais de
                        cardápios saudáveis com o objetivo de incentivar hábitos alimentares
                        mais equilibrados.
                    </p>

                    <p>
                        As informações disponibilizadas não constituem prescrição médica,
                        diagnóstico, tratamento ou aconselhamento profissional individualizado.
                    </p>

                    {/* 2️⃣ Não substituição profissional */}
                    <h3>2. Não Substituição de Profissionais de Saúde</h3>
                    <p>
                        O Health Pantry <strong>não substitui</strong> nutricionistas,
                        nutrólogos, médicos ou qualquer outro profissional de saúde
                        devidamente habilitado.
                    </p>

                    <p>
                        O usuário reconhece que qualquer decisão relacionada à sua saúde
                        deve ser discutida com um profissional qualificado.
                    </p>

                    {/* 3️⃣ Saúde e riscos pessoais */}
                    <h3>3. Saúde, Alergias e Condições Médicas</h3>
                    <p>
                        O usuário é integralmente responsável por considerar suas próprias
                        condições de saúde, incluindo, mas não se limitando a:
                        alergias alimentares, intolerâncias, doenças crônicas, restrições
                        alimentares, gestação, lactação ou qualquer condição médica específica.
                    </p>

                    <p>
                        O aplicativo não realiza validações clínicas nem garante que as
                        sugestões sejam adequadas para todos os perfis de usuários.
                    </p>

                    {/* 4️⃣ Limitação de responsabilidade */}
                    <h3>4. Limitação de Responsabilidade</h3>
                    <p>
                        O Health Pantry não garante resultados específicos, como emagrecimento,
                        ganho de massa muscular, melhora clínica ou qualquer outro resultado
                        relacionado à saúde.
                    </p>

                    <p>
                        O uso das informações é de inteira responsabilidade do usuário,
                        isentando o aplicativo, seus desenvolvedores e parceiros de quaisquer
                        danos diretos ou indiretos decorrentes do uso indevido das informações.
                    </p>

                    {/* 5️⃣ Uso adequado */}
                    <h3>5. Uso Adequado do Aplicativo</h3>
                    <p>
                        O aplicativo destina-se a usuários maiores de 18 anos ou menores
                        devidamente supervisionados por seus responsáveis legais.
                    </p>

                    <p>
                        O usuário compromete-se a utilizar o aplicativo com bom senso,
                        responsabilidade e consciência de suas limitações pessoais.
                    </p>

                    {/* 6️⃣ Versão gratuita vs premium */}
                    <h3>6. Versão Gratuita e Funcionalidades Futuras</h3>
                    <p>
                        A versão gratuita do aplicativo oferece apenas sugestões genéricas
                        de cardápio, sem personalização baseada em dados corporais,
                        clínicos ou nutricionais.
                    </p>

                    <p>
                        Funcionalidades adicionais, incluindo planos premium, poderão ser
                        disponibilizadas futuramente, com termos específicos próprios.
                    </p>

                    {/* 7️⃣ Atualizações e aceite */}
                    <h3>7. Atualização dos Termos</h3>
                    <p>
                        Estes Termos e Condições poderão ser atualizados periodicamente.
                        Sempre que houver alterações relevantes, um novo aceite será
                        solicitado ao usuário.
                    </p>

                    <p>
                        Ao aceitar estes termos, o usuário declara que leu, compreendeu
                        e concorda integralmente com todas as condições aqui descritas.
                    </p>
                </div>

                <label style={checkboxContainer}>
                    <input
                        type="checkbox"
                        disabled={!scrollFinal}
                        checked={confirmado}
                        onChange={(e) => setConfirmado(e.target.checked)}
                    />
                    <span style={{ marginLeft: 8 }}>
                        Li e concordo com os Termos e Condições
                    </span>
                </label>

                <button
                    disabled={!podeAceitar}
                    onClick={onAceitar}
                    style={{
                        ...botao,
                        background: podeAceitar ? "#28a745" : "#ccc",
                        cursor: podeAceitar ? "pointer" : "not-allowed",
                    }}
                >
                    ✅ Aceito os Termos
                </button>
            </div>
        </div>
    );
}

/* =========================
   ESTILOS
========================= */

const overlay = {
    position: "fixed",
    top: 0,
    left: 0,
    width: "100vw",
    height: "100vh",
    background: "rgba(0,0,0,0.7)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 9999,
};

const modal = {
    background: "#fff",
    borderRadius: 12,
    padding: 20,
    width: "90%",
    maxWidth: 520,
};

const conteudo = {
    maxHeight: 300,
    overflowY: "auto",
    marginBottom: 15,
};

const checkboxContainer = {
    display: "flex",
    alignItems: "center",
    marginBottom: 15,
    fontSize: 14,
};

const botao = {
    width: "100%",
    padding: 12,
    borderRadius: 8,
    border: "none",
    color: "#fff",
    fontSize: 16,
};