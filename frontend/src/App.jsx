import { useEffect, useState } from "react";
import Stocks from "./pages/Estoque";
import Cardapio from "./pages/Cardapio";
import ModalTermos from "./components/ModalTermos";
import ModalCadastroPerfil from "./components/ModalCadastroPerfil";
import Perfil from "./pages/Perfil";
import Loja from "./pages/Loja";

/* =========================
   CONFIG TERMOS
========================= */
const TERMOS_VERSAO_ATUAL = "1.2";

function App() {
  const [abaAtiva, setAbaAtiva] = useState("cardapio");
  const [erro, setErro] = useState(null);

  const [termosAceitos, setTermosAceitos] = useState(false);
  const [perfilCadastrado, setPerfilCadastrado] = useState(false);

  const [perfil, setPerfil] = useState(null);
  const [editarPerfil, setEditarPerfil] = useState(false);

  /* =========================
     VERIFICA TERMOS
  ========================= */
  useEffect(() => {
    const termosSalvos = localStorage.getItem("termos_aceitos");
    if (!termosSalvos) return;

    try {
      const dados = JSON.parse(termosSalvos);
      if (dados.aceito && dados.versao === TERMOS_VERSAO_ATUAL) {
        setTermosAceitos(true);
      }
    } catch {
      setTermosAceitos(false);
    }
  }, []);

  /* =========================
     VERIFICA PERFIL
  ========================= */
  useEffect(() => {
    const perfilSalvo = localStorage.getItem("perfil_usuario");
    if (perfilSalvo) {
      setPerfil(JSON.parse(perfilSalvo));
      setPerfilCadastrado(true);
    }
  }, []);

  /* =========================
     FETCH RECEITAS
  ========================= */
  useEffect(() => {
    fetch("http://127.0.0.1:8000/receitas")
      .then((res) => res.json())
      .catch(() => setErro("Erro ao carregar receitas"));
  }, []);

  /* =========================
     ACEITAR TERMOS
  ========================= */
  function aceitarTermos() {
    localStorage.setItem(
      "termos_aceitos",
      JSON.stringify({
        aceito: true,
        versao: TERMOS_VERSAO_ATUAL,
        data: new Date().toISOString(),
      })
    );
    setTermosAceitos(true);
  }

  /* =========================
     SALVAR PERFIL
  ========================= */
  function salvarPerfil(dadosPerfil) {
    localStorage.setItem("perfil_usuario", JSON.stringify(dadosPerfil));
    setPerfil(dadosPerfil);
    setPerfilCadastrado(true);
    setEditarPerfil(false);
  }

  /* =========================
     CAMPO PADRÃO
  ========================= */
  function campo(valor) {
    return valor ? valor : "—";
  }

  /* =========================
     CONTEÚDO DAS ABAS
  ========================= */
  function renderConteudo() {
    if (abaAtiva === "cardapio") return <Cardapio />;
    if (abaAtiva === "estoque") return <Stocks />;
    if (abaAtiva === "perfil") return <Perfil />;
    if (abaAtiva === "loja") return <Loja />;
  }
  /* =========================
     RENDER FINAL
  ========================= */
  return (
    <>
      {/* 1️⃣ TERMOS */}
      {!termosAceitos && (
        <ModalTermos onAceitar={aceitarTermos} />
      )}

      {/* 2️⃣ CADASTRO PERFIL */}
      {termosAceitos && !perfilCadastrado && (
        <ModalCadastroPerfil onSalvar={salvarPerfil} />
      )}

      {/* 2️⃣.1 EDIÇÃO PERFIL */}
      {editarPerfil && (
        <ModalCadastroPerfil
          onSalvar={salvarPerfil}
          dadosIniciais={perfil}
        />
      )}

      {/* 3️⃣ APP NORMAL */}
      {termosAceitos && perfilCadastrado && (
        <div style={appStyle}>
          <div style={conteudoStyle}>
            {erro ? erro : renderConteudo()}
          </div>

          <div style={tabBarStyle}>
            <Tab label="📅" ativo={abaAtiva === "cardapio"} onClick={() => setAbaAtiva("cardapio")} />
            <Tab label="📦" ativo={abaAtiva === "estoque"} onClick={() => setAbaAtiva("estoque")} />
            <Tab label="👤" ativo={abaAtiva === "perfil"} onClick={() => setAbaAtiva("perfil")} />
            <Tab label="🛒" ativo={abaAtiva === "loja"} onClick={() => setAbaAtiva("loja")} />
          </div>
        </div>
      )}
    </>
  );
}

function Tab({ label, ativo, onClick }) {
  return (
    <button
      onClick={onClick}
      style={{
        flex: 1,
        fontSize: 20,
        background: ativo ? "#E8F5E9" : "#fff",
        border: "none",
        padding: 10,
      }}
    >
      {label}
    </button>
  );
}

/* =========================
   ESTILOS
========================= */

const appStyle = {
  maxWidth: 480,
  margin: "0 auto",
  height: "100vh",
  display: "flex",
  flexDirection: "column",
};

const conteudoStyle = {
  flex: 1,
  padding: 16,
  overflowY: "auto",
};

const tabBarStyle = {
  display: "flex",
  borderTop: "1px solid #ccc",
};

export default App;