import React from "react";
import axios from "axios";
import { Button } from "@chakra-ui/react";
import { BsPlayFill } from "react-icons/bs";
import config from '../../config';


interface RunAlgoButtonProps {
	startDate: Date | null;
	endDate: Date | null;
	generations: number;
	percentage: number;
}

const RunAlgoButton: React.FC<RunAlgoButtonProps> = ({
	startDate,
	endDate,
	generations,
	percentage,
}) => {
	const runScript = () => {
		if (!startDate || !endDate) {
			alert("Please select both start and end dates.");
			return;
		}

		const formattedStartDate = startDate.toISOString().substring(0, 10);
		const formattedEndDate = endDate.toISOString().substring(0,10);


		const payload = {
			start_date: formattedStartDate,
			end_date: formattedEndDate,
			generation_number: generations,
			percentage,
		};
		(`${config.BASE_URL}endpoint`)
		axios
		//	.post("https://backend.sod3.eu/run-pygad/", payload)
			.post(`${config.BASE_URL}run-pygad/`, payload)
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
		<Button
			onClick={runScript}
			colorScheme="red"
			width="full"
			leftIcon={<BsPlayFill />}
			shadow="md"
			border="none"
			_hover={{
				bg: "red.500",
				transform: "translateY(-2px)",
				boxShadow: "lg",
			}}
		>
			Run PyGAD
		</Button>
	);
};

export default RunAlgoButton;
