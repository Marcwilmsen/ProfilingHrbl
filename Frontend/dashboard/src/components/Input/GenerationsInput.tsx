import React from "react";
import { FormControl, FormLabel, Input } from "@chakra-ui/react";

interface GenerationsInputProps {
	value: string;
	onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

const GenerationsInput: React.FC<GenerationsInputProps> = ({
	value,
	onChange,
}) => (
	<FormControl>
		<FormLabel htmlFor="generations">Generations</FormLabel>
		<Input
			id="generations"
			name="generation_number"
			type="number"
			value={value}
			onChange={onChange}
		/>
	</FormControl>
);

export default GenerationsInput;
