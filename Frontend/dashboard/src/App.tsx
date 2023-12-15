// App.tsx
import React from "react";
import { ChakraProvider } from "@chakra-ui/react";
import Sidemenu from "./components/Sidemenu/Sidemenu";
import Dashboard from "./components/Dashboard/Dashboard";

const App: React.FC = () => {
	return (
		<ChakraProvider>
			<Sidemenu />
			<Dashboard />
		</ChakraProvider>
	);
};

export default App;
