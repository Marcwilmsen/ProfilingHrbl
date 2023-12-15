import React from "react";
import { Button } from "@chakra-ui/react";
import { BsCloudDownloadFill } from "react-icons/bs";

// Define an interface for the component's props ss
interface DownloadButtonProps {
	downloadPath: string;
	fileName: string;
	buttonText: string;
}

const DownloadButton: React.FC<DownloadButtonProps> = ({
	downloadPath,
	fileName,
	buttonText,
}) => {
	return (
		<a
			href={downloadPath}
			download={fileName}
			style={{ textDecoration: "none" }}
		>
			<Button
				colorScheme="green"
				shadow="md"
				border="none"
				_hover={{
					bg: "green.500",
					transform: "translateY(-2px)",
					boxShadow: "lg",
				}}
			>
				<BsCloudDownloadFill style={{ marginRight: "5" }} />
				{buttonText}
			</Button>
		</a>
	);
};

export default DownloadButton;
