import { useEffect, useState } from "react";
import { StatusBar } from '@capacitor/status-bar';
import Stocks from "./pages/Estoque";
import Cardapio from "./pages/Cardapio";
import Header from "./components/Header";
import ModalTermos from "./components/ModalTermos";
import ModalCadastroPerfil from "./components/ModalCadastroPerfil";
import LoadingInicial from "./components/LoadingInicial";
import Perfil from "./pages/Perfil";
import Loja from "./pages/Loja";
import "./styles/global.css";
import CalendarioIcon from "./assets/icons/CalendarioIcon.png";
import LojaIcon from "./assets/icons/LojaIcon.png";
import EstoqueIcon from "./assets/icons/EstoqueIcon.png";
import PerfilIcon from "./assets/icons/PerfilIcon.png";
import { LocalNotifications } from '@capacitor/local-notifications';

/* =========================
   CONFIG TERMOS
========================= */
const TERMOS_VERSAO_ATUAL = "1.2";

async function solicitarPermissaoNotificacoes() {
  const perm = await LocalNotifications.requestPermissions();
  console.log("Permissão:", perm);

  return perm.display === 'granted';
}

function App() {
  const [loadingInicial, setLoadingInicial] = useState(true);
  const BASE_URL = "https://prealpha.onrender.com"
  const [abaAtiva, setAbaAtiva] = useState("cardapio");
  const [erro, setErro] = useState(null);

  const [termosAceitos, setTermosAceitos] = useState(false);
  const [perfilCadastrado, setPerfilCadastrado] = useState(false);

  const [perfil, setPerfil] = useState(null);
  const [editarPerfil, setEditarPerfil] = useState(false);

  const HORARIOS = { cafe: "08:00", almoco: "12:30", jantar: "19:00" };


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

  useEffect(() => {
    StatusBar.setOverlaysWebView({ overlay: false });
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

  /* =======================
     FETCH RECEITAS
  ========================= */
  useEffect(() => {
    fetch(`${BASE_URL}/receitas`)
      .then((res) => res.json())
      .catch(() => setErro("Erro ao carregar receitas"));
  }, []);

  /* LOADING INICIAL */
  useEffect(() => {
    const timer = setTimeout(() => {
      setLoadingInicial(false);
    }, 3000);

    return () => clearTimeout(timer);
  }, []);

  /* ✅ AGENDAR NOTIFICAÇÕES (CORRETO) */
  useEffect(() => {
    if (termosAceitos && perfilCadastrado) {
      agendarNotificacoes().catch(err =>
        console.error("Erro notificações:", err)
      );
    }
  }, [termosAceitos, perfilCadastrado]);

  /* 👇 SÓ DEPOIS o return */
  if (loadingInicial) {
    return <LoadingInicial />;
  }


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
        NOTIFICAÇÕES
  ========================= */


  async function agendarNotificacoes() {
    const permitido = await solicitarPermissaoNotificacoes();
    if (!permitido) return;

    // Cancela notificações antigas
    await LocalNotifications.cancel({
      notifications: [{ id: 1 }, { id: 2 }, { id: 3 }]
    });

    const hoje = new Date();
    const ids = [1, 2, 3];

    const notificacoes = Object.entries(HORARIOS).map(([refeicao, horario], index) => {
      const [h, m] = horario.split(":").map(Number);
      const dataNotificacao = new Date(hoje);
      dataNotificacao.setHours(h);
      dataNotificacao.setMinutes(m - 30);
      dataNotificacao.setSeconds(0);

      // Se já passou, agenda para amanhã
      if (dataNotificacao < new Date()) {
        dataNotificacao.setDate(dataNotificacao.getDate() + 1);
      }

      return {
        id: ids[index],
        title: `🍽 Hora do ${refeicao.charAt(0).toUpperCase() + refeicao.slice(1)}`,
        body: `Prepare-se para o ${refeicao}!`,
        schedule: { at: dataNotificacao },
        smallIcon: 'ic_launcher', // precisa existir no Android
        sound: 'default',
        // estilo de notificação grande
        extra: { bigText: `Não esqueça: o ${refeicao} começará em 30 minutos.` }
      };
    });

    await LocalNotifications.schedule({ notifications: notificacoes });
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
          <Header />
          <div style={conteudoStyle}>
            {erro ? erro : renderConteudo()}
          </div>

          <div style={tabBarStyle}>
            <Tab
              icon={CalendarioIcon}
              ativo={abaAtiva === "cardapio"}
              onClick={() => setAbaAtiva("cardapio")}
            />

            <Tab
              icon={EstoqueIcon}
              ativo={abaAtiva === "estoque"}
              onClick={() => setAbaAtiva("estoque")}
            />

            <Tab
              icon={PerfilIcon}
              ativo={abaAtiva === "perfil"}
              onClick={() => setAbaAtiva("perfil")}
            />

            <Tab
              icon={LojaIcon}
              ativo={abaAtiva === "loja"}
              onClick={() => setAbaAtiva("loja")}
            />
          </div>
        </div>
      )}
    </>
  );
}

function Tab({ icon, ativo, onClick }) {
  return (
    <button
      onClick={onClick}
      style={{
        flex: 1,
        background: ativo ? "#E8F5E9" : "#fff",
        border: "none",
        padding: 10,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <img
        src={icon}
        alt="icon"
        style={{
          width: 24,
          height: 24,
          transition: "0.2s",
          filter: ativo
            ? "none"
            : "grayscale(100%) opacity(0.5)",
        }}
      />
    </button>
  );
}

/* =========================
   ESTILOS
========================= */

const appStyle = {
  maxWidth: 480,
  margin: "0 auto",
  Height: "100vh",
  display: "flex",
  flexDirection: "column",
};

const conteudoStyle = {
  flex: 1,
  padding: 16,
  overflowY: "auto",
  paddingBottom: `calc(80px + env(safe-area-inset-bottom))`
};

const tabBarStyle = {
  position: "fixed",
  bottom: 0,
  left: 0,
  right: 0,
  display: "flex",
  borderTop: "1px solid #ccc",
  background: "#fff",
  zIndex: 1000,
  paddingBottom: "env(safe-area-inset-bottom)"
};

export default App;