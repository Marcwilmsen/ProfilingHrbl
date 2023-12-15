import React, { useRef, useState } from "react";
import {
	Button,
	Input,
	useToast,
	FormControl,
	FormLabel,
	InputGroup,
	InputRightElement,
	Box,
	HStack,
} from "@chakra-ui/react";

interface InputFileButtonProps {
	uploadUrl: string;
	acceptedFiles: string;
	label: string;
}

function InputFileButton({
	uploadUrl,
	acceptedFiles,
	label,
}: InputFileButtonProps) {
	const [file, setFile] = useState<File | null>(null);
	const [uploading, setUploading] = useState<boolean>(false);
	const toast = useToast();
	const fileInputRef = useRef<HTMLInputElement>(null);

	const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
		const files = event.target.files;
		if (files) {
			setFile(files[0]);
		}
	};

	const handleUpload = async () => {
		if (!file) {
			toast({
				title: "Error",
				description: "Please select a file first!",
				status: "error",
				duration: 5000,
				isClosable: true,
			});
			return;
		}

		const formData = new FormData();
		formData.append("file", file);
		formData.append("name", file.name);

		setUploading(true);

		try {
			const response = await fetch(uploadUrl, {
				method: "POST",
				body: formData,
			});

			if (response.ok) {
				toast({
					title: "Success",
					description: "File is being processed.",
					status: "success",
					duration: 5000,
					isClosable: true,
				});
			} else {
				const errorMessage = await response.text();
				toast({
					title: "Error",
					description: `There was an issue with the file upload: ${errorMessage}`,
					status: "error",
					duration: 5000,
					isClosable: true,
				});
			}
		} catch (error) {
			console.error("Error during the upload:", error);
			toast({
				title: "Error",
				description: "An error occurred while uploading the file.",
				status: "error",
				duration: 5000,
				isClosable: true,
			});
		} finally {
			setUploading(false);
		}
	};

	const triggerFileInput = () => {
		fileInputRef.current?.click();
	};

	return (
		<Box maxW="lg" p={1}>
			<FormControl>
				<FormLabel htmlFor="file-upload">{label}</FormLabel>
				<HStack spacing={2}>
					<InputGroup>
						<Input
							type="file"
							id="file-upload"
							ref={fileInputRef}
							onChange={handleFileChange}
							accept={acceptedFiles}
							hidden
						/>
						<Input placeholder={file ? file.name : "No file chosen"} readOnly />
						<InputRightElement width="4.5rem" mr={1}>
							<Button
								h="1.75rem"
								size="sm"
								onClick={triggerFileInput}
								colorScheme="blue"
								_hover={{
									bg: "blue.500",
									transform: "translateY(-2px)",
									boxShadow: "lg",
								}}
							>
								Browse
							</Button>
						</InputRightElement>
					</InputGroup>
					<Button
						onClick={handleUpload}
						isLoading={uploading}
						loadingText="Uploading"
						colorScheme="blue"
						size="md"
						shadow="md"
						_hover={{
							bg: "blue.500",
							transform: "translateY(-2px)",
							boxShadow: "lg",
						}}
					>
						Upload
					</Button>
				</HStack>
			</FormControl>
		</Box>
	);
}

export default InputFileButton;
