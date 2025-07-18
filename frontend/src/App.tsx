import { Login } from "./pages/LoginPage";
import { Chat } from "./pages/ChatPage";
import "./index.css";

import logo from "./logo.svg";
import reactLogo from "./react.svg";

export function App() {
  let content;
  let isLoggedIn = false;

  if (isLoggedIn) {
    content = <Chat />;
  } else {
    content = <Login />;
  }

  return (
    <div className="app">
      {content}
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
