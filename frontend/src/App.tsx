import React, { useState } from "react";
// import { Login } from "./pages/LoginPage";
// import { Chat } from "./pages/ChatPage";
import LoginPage from "./pages/LoginPage";
import ChatPage from "./pages/ChatPage";
import "./index.css";

import logo from "./logo.svg";
import reactLogo from "./react.svg";

export function App() {
  let content;
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const handleLoginSuccess = () => {
    setIsLoggedIn(true);
  };

  return (
    <div className="app">
      {content}
      {isLoggedIn ? (
        <ChatPage />
      ) : (
        <LoginPage onLoginSuccess={handleLoginSuccess} />
      )}
    </div>

    // <div className="app">
    //   <div className="logo-container">
    //     <img src={logo} alt="Bun Logo" className="logo bun-logo" />
    //     <img src={reactLogo} alt="React Logo" className="logo react-logo" />
    //   </div>

    //   <h1>Bun + React</h1>
    //   <p>
    //     Edit <code>src/App.tsx</code> and save to test HMR
    //   </p>
    //   <APITester />
    // </div>
  );
}

export default App;