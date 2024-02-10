import React from "react";
import { Button } from "@chakra-ui/react";
import { BsCloudDownloadFill } from "react-icons/bs";

// Extend the interface to include an optional width prop
interface DownloadButtonProps {
	downloadPath: string;
	fileName: string;
	buttonText: string;
	width?: string; // Add a width prop
}

const DownloadButton: React.FC<DownloadButtonProps> = ({
	downloadPath,
	fileName,
	buttonText,
	width = "auto", // Default to "auto" if not provided
}) => {
	return (
		<a
			href={downloadPath}
			download={fileName}
			style={{ textDecoration: "none", width: "100%" }}
		>
			{" "}
			{/* Ensure the anchor tag also takes full width */}
			<Button
				colorScheme="green"
				shadow="md"
				border="none"
				w={width} // Apply the width prop to the Button
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
