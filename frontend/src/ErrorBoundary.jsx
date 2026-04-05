import React from "react";

export default class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, info: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, info) {
        console.error("Erro capturado pelo ErrorBoundary:", error, info);
        this.setState({ error, info });
    }

    render() {
        if (this.state.hasError) {
            return (
                <div
                    style={{
                        padding: 20,
                        color: "#fff",
                        backgroundColor: "red",
                        fontFamily: "monospace",
                        whiteSpace: "pre-wrap",
                    }}
                >
                    <h2>Ocorreu um erro no app!</h2>
                    <strong>{this.state.error?.toString()}</strong>
                    <pre>{this.state.info?.componentStack}</pre>
                </div>
            );
        }
        return this.props.children;
    }
}