import React from "react";
import { ChakraProvider } from "@chakra-ui/react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Sidemenu from "./components/Sidemenu/Sidemenu";
import Dashboard from "./components/Pages/Dashboard";
import MasterAreaOne from "./components/Pages/MasterAreaOne";
import MasterAreaFour from "./components/Pages/MasterAreaFour";
import MasterAreaThree from "./components/Pages/MasterAreaThree";
import MasterAreaTwo from "./components/Pages/MasterAreaTwo";
import ResultsPage from "./components/Pages/ResultsPage";
import WarehouseSolutionProfiles from "./components/Pages/WarehouseSolutionProfiles";
import WarehouseSolutionProfileDetailsPage from "./components/Pages/WarehouseSolutionProfileDetail";
import ConsolePage from "./components/Pages/ConsoleComponent";
import Analytics from "./components/Pages/Analytics";

const App: React.FC = () => {
	return (
		<ChakraProvider>
			<Router>
				<Sidemenu />
				<Routes>
					<Route path="/" element={<Dashboard />} />
					<Route path="/master-one" element={<MasterAreaOne />} />
					<Route path="/master-two" element={<MasterAreaTwo />} />
					<Route path="/master-three" element={<MasterAreaThree />} />
					<Route path="/master-four" element={<MasterAreaFour />} />
					<Route path="/analytics" element={<Analytics />} />
					<Route path="/results" element={<ResultsPage />} />
					<Route path="/warehouse-solution-profiles" element={<WarehouseSolutionProfiles />} />
					<Route path="/warehouse-solution-profiles/:id" element={<WarehouseSolutionProfileDetailsPage />} />
					<Route path="/backend-consol-page" element={<ConsolePage />} />
				</Routes>
			</Router>
		</ChakraProvider>
	);
};

export default App;
