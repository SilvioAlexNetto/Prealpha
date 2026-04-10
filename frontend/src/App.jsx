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


function getDataKey(date) {
  return date.toISOString().split("T")[0];
}

function calcularStreak(progresso, freezeDisponivel, freezeUsados) {
  let streak = 0;
  let data = new Date();
  let freezeUsado = 0;

  let limite = 3650; // ~10 anos

  while (limite--) {
    const key = getDataKey(data);
    const dia = progresso[key];

    const completo =
      dia?.cafe &&
      dia?.almoco &&
      dia?.jantar;

    if (completo) {
      streak++;
    } else {
      if (!freezeUsados[key] && freezeUsado < freezeDisponivel) {
        freezeUsado++;
        freezeUsados[key] = true; // 🔥 marca uso
      } else {
        break;
      }
    }

    data.setDate(data.getDate() - 1);
  }

  return { streak, freezeUsado, freezeUsados };
}

function App() {
  const [loadingInicial, setLoadingInicial] = useState(true);
  const BASE_URL = "https://prealpha.onrender.com"
  const [abaAtiva, setAbaAtiva] = useState("cardapio");
  const [erro, setErro] = useState(null);
  const [streak, setStreak] = useState(0);
  const [streakAnimando, setStreakAnimando] = useState(false);
  const [termosAceitos, setTermosAceitos] = useState(false);
  const [perfilCadastrado, setPerfilCadastrado] = useState(false);
  const [mostrarCompartilhar, setMostrarCompartilhar] = useState(null);
  const [perfil, setPerfil] = useState(null);
  const [editarPerfil, setEditarPerfil] = useState(false);

  const HORARIOS = { cafe: "08:00", almoco: "12:30", jantar: "19:00" };

  const [freeze, setFreeze] = useState(() => {
    return Number(localStorage.getItem("freeze")) || 1;
  });
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


  useEffect(() => {
    localStorage.setItem("freeze", freeze);
  }, [freeze]);

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

  useEffect(() => {
    const atualizar = () => {
      let progresso = {};

      try {
        progresso = JSON.parse(localStorage.getItem("progresso")) || {};
      } catch {
        progresso = {};
      }

      const freezeUsadosSalvo = JSON.parse(localStorage.getItem("freeze_usados") || "{}");

      const { streak: novo, freezeUsado, freezeUsados } =
        calcularStreak(progresso, freeze, freezeUsadosSalvo);

      localStorage.setItem("freeze_usados", JSON.stringify(freezeUsados));

      setStreak(prev => {
        if (novo > prev) {
          triggerStreakAnimacao();

          const marcos = [1, 7, 14, 21, 30];

          if (marcos.includes(novo)) {
            const chave = `streak_${novo}_mostrado`;
            const jaMostrou = localStorage.getItem(chave);

            if (!jaMostrou) {
              setMostrarCompartilhar(novo);
              localStorage.setItem(chave, "true");
            }
          }
        }
        return novo;
      });

      const novosUsos = Object.keys(freezeUsados).filter(
        key => !freezeUsadosSalvo[key]
      );

      if (novosUsos.length > 0) {
        setFreeze(prev => Math.max(prev - novosUsos.length, 0));
      }
    };

    window.addEventListener("streakAtualizado", atualizar);

    atualizar(); // roda ao iniciar

    return () => {
      window.removeEventListener("streakAtualizado", atualizar);
    };
  }, [freeze]);


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

  function triggerStreakAnimacao() {
    setStreakAnimando(true);

    // vibração (mobile)
    if (navigator.vibrate) {
      navigator.vibrate(100);
    }

    setTimeout(() => {
      setStreakAnimando(false);
    }, 800);
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

  async function compartilharStreak() {
    const texto = `🔥 ${mostrarCompartilhar} dias seguidos! 💪 Foco total na alimentação`

    if (navigator.share) {
      try {
        await navigator.share({
          title: "Meu streak 🔥",
          text: texto,
          url: window.location.href
        });
      } catch (err) {
        console.log("Erro ao compartilhar", err);
      }
    } else {
      navigator.clipboard.writeText(texto);
      alert("Texto copiado!");
    }
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
        smallIcon: 'ic_stat_logo', // precisa existir no Android
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
          <div style={{
            ...streakStyle,
            transform: streakAnimando
              ? "translateX(-50%) scale(1.1)"
              : "translateX(-50%)"
          }}>
            <span className={streakAnimando ? "streak-pop" : ""}>
              🔥 {streak} dias
            </span>
          </div>

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
          {mostrarCompartilhar && (
            <div style={overlayStyle}>
              <div style={modalStyle}>
                <h3>🔥 {mostrarCompartilhar} dias seguidos!</h3>

                <img
                  src={`/streak${mostrarCompartilhar}.png`}
                  alt="Compartilhar streak"
                  style={{ width: "100%", borderRadius: 12 }}
                />

                <button onClick={compartilharStreak}>
                  📤 Compartilhar
                </button>

                <button onClick={() => setMostrarCompartilhar(null)}>
                  Fechar
                </button>
              </div>
            </div>
          )}
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
  height: "100vh",
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

const streakStyle = {
  position: "fixed",
  top: 110,
  left: "50%",
  transform: "translateX(-50%)",
  background: "#111",
  color: "#fff",
  padding: "6px 14px",
  borderRadius: 20,
  fontSize: 14,
  fontWeight: "bold",
  boxShadow: "0 0 10px rgba(255,120,0,0.4)",
  zIndex: 999,
  transition: "0.2s",
};

const overlayStyle = {
  position: "fixed",
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  background: "rgba(0,0,0,0.6)",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  zIndex: 2000
};

const modalStyle = {
  background: "#fff",
  padding: 20,
  borderRadius: 16,
  width: "90%",
  maxWidth: 350,
  textAlign: "center"
};

export default App;