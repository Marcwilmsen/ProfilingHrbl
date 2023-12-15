import axios from "axios";
import { Button } from "@chakra-ui/react";
import { BsPlayFill } from "react-icons/bs";

function RunAlgoBtn() {
	const runScript = () => {
		axios
			.post("http://127.0.0.1:8000/run-pygad/")
			.then((response) => {
				console.log(response.data.output);
				if (response.data.error) {
					console.error("Run Algo Error:", response.data.error);
				}
			})
			.catch((error) => {
				console.error("An error occurred:", error);
			});
	};

	return (
		<div>
			<Button
				onClick={runScript}
				colorScheme="red"
				shadow="md"
				border={"none"}
				_hover={{
					bg: "red.500",
					transform: "translateY(-2px)",
					boxShadow: "lg",
				}}
			>
				<BsPlayFill style={{ marginRight: "5" }} />
				Run PyGAD
			</Button>
		</div>
	);
}

export default RunAlgoBtn;
