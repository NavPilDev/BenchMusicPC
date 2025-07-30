import "./App.css";
import Navbar from "./components/Navbar";
import Transfer from "./pages/transfer/transfer";
import Reccomend from "./pages/reccomend/reccomend";
import Home from "./pages/home/home";
import React from "react";
import { Route, Routes } from "react-router-dom";

import styles from "./global.module.css";

function App() {
  return (
    <div className={styles.page}>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/transfer" element={<Transfer />} />
        <Route path="/reccomend" element={<Reccomend />} />
      </Routes>
      {/* <div className="container">
      </div> */}
    </div>
  );
}

export default App;