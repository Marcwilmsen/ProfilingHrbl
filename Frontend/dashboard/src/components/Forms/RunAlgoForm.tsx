import React, { useState } from "react";
import {
	FormControl,
	FormLabel,
	Input,
	Grid,
	Box,
	VStack,
} from "@chakra-ui/react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import RunAlgoButton from "../Buttons/RunAlgoButton";
import ShowSolutionButton from "../Buttons/ShowSolutionButton";

const RunAlgorithmForm: React.FC = () => {
	const [startDate, setStartDate] = useState<Date | null>(null);
	const [endDate, setEndDate] = useState<Date | null>(null);
	const [generations, setGenerations] = useState<string>("");
	const [percentage, setPercentage] = useState<string>("");

	const numericGenerations = generations ? parseInt(generations) : 0;
	const numericPercentage = percentage ? parseInt(percentage) : 0;

	const labelHeight = "32px";

	const customInputStyle = {
		borderColor: "gray.300",
		_hover: { borderColor: "gray.400" },
		_focus: { boxShadow: "outline", borderColor: "blue.500" },
	};

	return (
		<Box>
			<Grid templateColumns="repeat(8, 1fr)" gap={4}>
				<FormControl gridColumn="span 2">
					<FormLabel htmlFor="generations">Generations</FormLabel>
					<Input
						id="generations"
						name="generations"
						type="number"
						value={generations}
						onChange={(e) => setGenerations(e.target.value)}
					/>
				</FormControl>

				<FormControl gridColumn="span 2">
					<FormLabel htmlFor="startDate">Start Date</FormLabel>
					<DatePicker
						selected={startDate}
						onChange={setStartDate}
						dateFormat="yyyy-MM-dd"
						customInput={<Input {...customInputStyle} />}
					/>
				</FormControl>

				<VStack gridColumn="span 4" spacing={0} align="stretch">
					<Box height={labelHeight} />
					<RunAlgoButton
						startDate={startDate}
						endDate={endDate}
						generations={numericGenerations}
						percentage={numericPercentage}
					/>
				</VStack>

				<FormControl gridColumn="span 2">
					<FormLabel htmlFor="percentage">Percentage</FormLabel>
					<Input
						id="percentage"
						name="percentage"
						type="number"
						value={percentage}
						onChange={(e) => setPercentage(e.target.value)}
					/>
				</FormControl>

				<FormControl gridColumn="span 2">
					<FormLabel htmlFor="endDate">End Date</FormLabel>
					<DatePicker
						selected={endDate}
						onChange={setEndDate}
						dateFormat="yyyy-MM-dd"
						customInput={<Input {...customInputStyle} />}
					/>
				</FormControl>

				<VStack gridColumn="span 4" spacing={0}>
					<Box height={labelHeight} />
					<ShowSolutionButton
						pagePath={"/warehouse-solution-profiles"}
						buttonText={"Get Results"}
					/>
				</VStack>
			</Grid>
		</Box>
	);
};

export default RunAlgorithmForm;
