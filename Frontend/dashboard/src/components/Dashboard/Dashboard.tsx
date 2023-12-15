import { Box, Card, HStack, VStack } from "@chakra-ui/react";
import InputFileButton from "../InputFileButton/InputFileButton";
import RunAlgoBtn from "../RunAlgoBtn/RunAlgoBtn";
import DownloadButton from "../DownloadButton/DownloadButton";

const Dashboard: React.FC = () => {
	return (
		<>
			<Box width="80%" position="absolute" top="0" right="0" mt={5}>
				<HStack spacing={4} align="center" justify="left">
					<Card bg="white" p={3} m={1} height="130px">
						<InputFileButton
							uploadUrl={"http://0.0.0.0:8080/upload/pickdata/"}
							acceptedFiles={".csv"}
							label={"Upload Pickdata .CSV"}
						/>
					</Card>

					<Card bg="white" p={3} m={1} height="130px">
						<InputFileButton
							uploadUrl={"http://0.0.0.0:8080/upload/pickdata/"}
							acceptedFiles={".xlsx"}
							label={"Upload Masterlist Excel Sheet"}
						/>
					</Card>

					<Card bg="white" p={3} m={1} height="130px">
						<VStack spacing={4} align="left" justify="center" height="100%">
							<DownloadButton
								downloadPath={"pickdata.txt"}
								fileName={"pickdata.txt"}
								buttonText={"Download Pickdata"}
							/>
							<HStack spacing={4}>
								<DownloadButton
									downloadPath={"new_masterlist.xlsx"}
									fileName={"new_masterlist.xlsx"}
									buttonText={"Download Masterlist"}
								/>

								<RunAlgoBtn />
							</HStack>
						</VStack>
					</Card>
				</HStack>

				<iframe
					src="https://grafana.sod3.eu/public-dashboards/a83fd7734d6744d686f6884a2d2ecf7f"
					width="90%"
					height="1000px"
					title="Grafana Dashboard"
				></iframe>
			</Box>
		</>
	);
};

export default Dashboard;
