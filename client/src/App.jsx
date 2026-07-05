import { BrowserRouter, Routes, Route } from "react-router-dom"
import TrainPage from "./pages/TrainPage"
import PredictPage from "./pages/PredictPage"
import Navbar from "./components/Navbar"
import "./App.css"

function App() {
  return (
    <BrowserRouter>

      
      <div className="app-container">

        <Navbar/>

        <Routes>
          <Route path="/" element={<PredictPage />} />
          <Route path="/train" element={<TrainPage />} />
        </Routes>

      </div>

    </BrowserRouter>
  )
}

export default App