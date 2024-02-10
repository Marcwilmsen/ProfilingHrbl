import React from "react";
import { FormControl, FormLabel, Input } from "@chakra-ui/react";

interface PercentageInputProps {
	value: string;
	onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

const PercentageInput: React.FC<PercentageInputProps> = ({
	value,
	onChange,
}) => (
	<FormControl>
		<FormLabel htmlFor="percentage">Percentage</FormLabel>
		<Input
			id="percentage"
			name="percentage"
			type="number"
			value={value}
			onChange={onChange}
		/>
	</FormControl>
);

export default PercentageInput;
