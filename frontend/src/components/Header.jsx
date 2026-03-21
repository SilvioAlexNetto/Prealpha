import "./Header.css";
import Logo from "../assets/icons/Logo.png";
import DuvidaIcon from "../assets/icons/DuvidaIcon.png";

export default function Header() {
    return (
        <div className="hp-header">

            <div className="hp-header-left">
                <img src={Logo} className="hp-header-logo" />
                <h1 className="hp-header-title">Health Pantry</h1>
            </div>

            <button
                className="hp-header-help"
                onClick={() => alert("Ajuda em breve")}
            >
                <img src={DuvidaIcon} alt="Ajuda" />
            </button>

        </div>
    );
}

